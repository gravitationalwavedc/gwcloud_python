import requests
import json
import jwt
from gwdc_python import GWDC
from graphene_file_upload import utils

from .bilby_job import BilbyJob

GWCLOUD_ENDPOINT = 'https://gwcloud.org.au/bilby/graphql'

class GWCloud:
    def __init__(self, token, endpoint=GWCLOUD_ENDPOINT):
        self.client = GWDC(token=token, endpoint=endpoint)

    def start_bilby_job(self, job_name, job_description, private, ini):
        query = """
            mutation NewBilbyJobFromIniString($input: BilbyJobFromIniStringMutationInput!){
                newBilbyJobFromIniString (input: $input) {
                    result
                }
            }
        """

        variables = {
            "input": {
                "start": {
                    "name": job_name,
                    "description": job_description,
                    "private": private
                },
                "iniString": ini
            }
        }

        return self.client.request(query=query, variables=variables)

    def get_preferred_job_list(self):
        return self._get_public_jobs(search="preferred", time_range="Any time")

    def _get_public_jobs(self, search="", time_range="Any time", number=100):
        query = """
            query ($search: String, $timeRange: String, $first: Int){
                publicBilbyJobs (search: $search, timeRange: $timeRange, first: $first) {
                    edges {
                        node {
                            id
                            user
                            name
                            description
                        }
                    }
                }
            }
        """

        variables = {
            "search": search,
            "timeRange": time_range,
            "first": number
        }

        data, errors = self.client.request(query=query, variables=variables)

        return [BilbyJob(**job['node']) for job in data['publicBilbyJobs']['edges']], errors


    def _get_job_by_id(self, id):
        query = """
            query ($id: ID!){
                bilbyJob (id: $id) {
                    name
                    userId
                    description
                }
            }
        """

        variables = {
            "id": id
        }

        data, errors = self.client.request(query=query, variables=variables)

        return BilbyJob(**data['bilbyJob']), errors

    def _get_user_jobs(self):
        query = """
            query {
                bilbyJobs {
                    edges {
                        node {
                            id
                            name
                            userId
                            description
                        }
                    }
                }
            }
        """
        
        data, errors = self.client.request(query=query)

        return [BilbyJob(**job['node']) for job in data['bilbyJobs']['edges']], errors
