from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, GroupItem, UserItem, PaginationItem
import logging

logger = logging.getLogger('tableau.endpoint.groups')


class Groups(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.parent_srv = parent_srv

    @property
    def baseurl(self):
        return "{0}/sites/{1}/groups".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all groups
    def get(self, req_options=None):
        logger.info('Querying all groups on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_group_items = GroupItem.from_response(server_response.content)
        return all_group_items, pagination_item

    # Gets all users in a given group
    def populate_users(self, group_item, req_options=None):
        if not group_item.id:
            error = "Group item missing ID. Group must be retrieved from server first."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/users".format(self.baseurl, group_item.id)
        server_response = self.get_request(url, req_options)
        group_item._set_users(UserItem.from_response(server_response.content))
        pagination_item = PaginationItem.from_response(server_response.content)
        logger.info('Populated users for group (ID: {0})'.format(group_item.id))
        return pagination_item

    # Deletes 1 group by id
    def delete(self, group_id):
        if not group_id:
            error = "Group ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, group_id)
        self.delete_request(url)
        logger.info('Deleted single group (ID: {0})'.format(group_id))

    # Removes 1 user from 1 group
    def remove_user(self, group_item, user_id):
        user_set = group_item.users
        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/users/{2}".format(self.baseurl, group_item.id, user_id)
        self.delete_request(url)
        for user in user_set:
            if user.id == user_id:
                user_set.remove(user)
                break
        logger.info('Removed user (id: {0}) from group (ID: {1})'.format(user_id, group_item.id))

    # Adds 1 user to 1 group
    def add_user(self, group_item, user_id):
        user_set = group_item.users
        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/users".format(self.baseurl, group_item.id)
        add_req = RequestFactory.Group.add_user_req(user_id)
        server_response = self.post_request(url, add_req)
        new_user = UserItem.from_response(server_response.content).pop()
        user_set.add(new_user)
        group_item._set_users(user_set)
        logger.info('Added user (id: {0}) to group (ID: {1})'.format(user_id, group_item.id))
