from helpers.url_utils import add_query_parameters

if __name__ == '__main__':

        base_url = "http://localhost:8080/api/v1/dataresources/"
        identifier = "1234-5678"
        query_params = [
                {"name": "firstname", "value": None},
                {"name": "lastname", "value": None},
                {"name": "page", "value": None},
                {"name": "size", "value": None}
        ]

        print(add_query_parameters(base_url, None, None))
        exit(2)

