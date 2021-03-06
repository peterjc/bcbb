"""Access Galaxy via the standard API.
"""
import urllib
import urllib2
import json

class GalaxyApiAccess:
    """Simple front end for accessing Galaxy's REST API.
    """
    def __init__(self, galaxy_url, api_key):
        self._base_url = galaxy_url
        self._key = api_key

    def _make_url(self, rel_url, params=None):
        if not params:
            params = dict()
        params['key'] = self._key
        vals = urllib.urlencode(params)
        return ("%s%s" % (self._base_url, rel_url), vals)

    def _get(self, url, params=None):
        url, params = self._make_url(url, params)
        response = urllib2.urlopen("%s?%s" % (url, params))
        return json.loads(response.read())

    def _post(self, url, data, params=None, need_return=True):
        url, params = self._make_url(url, params)
        request = urllib2.Request("%s?%s" % (url, params),
                headers = {'Content-Type' : 'application/json'},
                data = json.dumps(data))
        response = urllib2.urlopen(request)
        try:
            data = json.loads(response.read())
        except ValueError:
            if need_return:
                raise
            else:
                data = {}
        return data

    def get_libraries(self):
        return self._get("/api/libraries")

    def show_library(self, library_id):
        return self._get("/api/libraries/%s" % library_id)

    def create_library(self, name, descr="", synopsis=""):
        return self._post("/api/libraries", data = dict(name=name,
            description=descr, synopsis=synopsis))

    def library_contents(self, library_id):
        return self._get("/api/libraries/%s/contents" % library_id)

    def create_folder(self, library_id, parent_folder_id, name, descr=""):
        return self._post("/api/libraries/%s/contents" % library_id,
                data=dict(create_type="folder", folder_id=parent_folder_id,
                          name=name, description=descr))

    def show_folder(self, library_id, folder_id):
        return self._get("/api/libraries/%s/contents/%s" % (library_id,
            folder_id))

    def upload_directory(self, library_id, folder_id, directory, dbkey,
            access_role='', file_type='auto', link_data_only=True):
        """Upload a directory of files with a specific type to Galaxy.
        """
        return self._post("/api/libraries/%s/contents" % library_id,
                data=dict(create_type='file', upload_option='upload_directory',
                    folder_id=folder_id, server_dir=directory,
                    dbkey=dbkey, roles=str(access_role),
                    file_type=file_type, link_data_only=str(link_data_only)),
                need_return=False)

    def run_details(self, run_bc, run_date=None):
        """Next Gen LIMS specific API functionality.
        """
        try:
            details = self._get("/nglims/api_run_details", dict(run=run_bc))
        except ValueError:
            raise ValueError("Could not find information in Galaxy for run: %s" % run_bc)
        if details.has_key("error") and run_date is not None:
            try:
                details = self._get("/nglims/api_run_details", dict(run=run_date))
            except ValueError:
                raise ValueError("Could not find information in Galaxy for run: %s" % run_date)
        return details

    def sequencing_projects(self):
        """Next Gen LIMS: retrieve summary information of sequencing projects.
        """
        return self._get("/nglims/api_projects")

    def sqn_run_summary(self, run_info):
        """Next Gen LIMS: Upload sequencing run summary information.
        """
        return self._post("/nglims/api_upload_sqn_run_summary",
                data=run_info)

    def sqn_report(self, start_date, end_date):
        """Next Gen LIMS: report of items sequenced in a time period.
        """
        return self._get("/nglims/api_sqn_report",
                dict(start=start_date, end=end_date))

