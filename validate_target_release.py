import os
import requests
import sys

ORG_URL = 'https://dev.azure.com/EmersonPSS'
PROJECT = 'PSS'
REPO = 'DeltaV_Core'
TOKEN = os.environ['SYSTEM_ACCESSTOKEN']
TARGET_RELEASE_REQUIRED = os.environ['TARGET_RELEASE_REQUIRED']

HEADERS = {"Content-Type": "application/json"}
AUTH = ('', TOKEN)
BASE_URL = f"{ORG_URL}/{PROJECT}/_apis"

def fail_pipeline(msg):
    print(f"##vso[task.logissue type=error]{msg}")
    print("##vso[task.complete result=Failed;]Validation failed.")
    sys.exit(1)

def get_pr_id():
    pr_id = os.environ.get('SYSTEM_PULLREQUEST_PULLREQUESTID', '')
    if not pr_id:
        fail_pipeline("No PR context found.")
    return pr_id

def get_linked_work_items(pr_id):
    url = f"{BASE_URL}/git/repositories/{REPO}/pullRequests/{pr_id}/workitems?api-version=7.0"
    r = requests.get(url, headers=HEADERS, auth=AUTH)
    r.raise_for_status()
    return r.json().get('value', [])

def get_work_item_and_parents(work_item_id, seen=None):
    if seen is None:
        seen = set()
    if work_item_id in seen:
        return []
    seen.add(work_item_id)
    url = f"{BASE_URL}/wit/workitems/{work_item_id}?$expand=relations&api-version=7.0"
    r = requests.get(url, headers=HEADERS, auth=AUTH)
    r.raise_for_status()
    wi = r.json()
    items = [wi]
    for rel in wi.get('relations', []):
        if rel['rel'] == 'System.LinkTypes.Hierarchy-Reverse':
            parent_id = int(rel['url'].split('/')[-1])
            items += get_work_item_and_parents(parent_id, seen)
    return items

def validate(items):
    for wi in items:
        fields = wi.get('fields', {})
        if fields.get('Emerson.TargetRelease') == TARGET_RELEASE_REQUIRED:
            return True
    return False

pr_id = get_pr_id()
print(f"Validating PR #{pr_id}...")

linked = get_linked_work_items(pr_id)
if not linked:
    fail_pipeline(f"PR #{pr_id} has no linked work items.")

all_items = []
for item in linked:
    wi_id = int(item['url'].split('/')[-1])
    all_items.extend(get_work_item_and_parents(wi_id))

if validate(all_items):
    print("✅ Target Release is valid")
else:
    fail_pipeline(f"❌ No linked work item has Target Release == {TARGET_RELEASE_REQUIRED}.")
