import json
import names
import random
import uuid
from ldclient import Context

'''
Construct a user context
'''
def create_user_context():
  user_key = "usr-" + str(uuid.uuid4())
  name = f'{names.get_first_name()} {names.get_last_name()}'
  plan = random.choice(['platinum', 'silver', 'gold', 'diamond', 'free'])
  role = random.choice(['reader', 'writer', 'admin'])
  metro = random.choice(['New York', 'Chicago', 'Minneapolis', 'Atlanta', 'Los Angeles', 'San Francisco', 'Denver', 'Boston'])

  def beta_chance():
    if random.randint(1, 10) <= 3:
      return True
    else:
      return False

  user_context = Context.builder(user_key) \
  .set("kind", "user") \
  .set("name", name) \
  .set("plan", plan) \
  .set("role", role) \
  .set("metro", metro) \
  .set("beta", beta_chance()) \
  .build()

  return user_context

'''
Construct a device context
'''
def create_device_context():
  device_key = "dvc-" + str(uuid.uuid4())
  os = random.choice(['Android', 'iOS', 'Mac OS', 'Windows'])
  version = random.choice(['1.0.2', '1.0.4', '1.0.7', '1.1.0', '1.1.5'])
  type = random.choice(['Fire TV', 'Roku', 'Hisense', 'Comcast', 'Verizon', 'Browser'])

  device_context = Context.builder(device_key) \
  .set("kind", "device") \
  .set("os", os) \
  .set("type", type) \
  .set("version", version) \
  .build()

  return device_context


'''
Construct an organization context
'''
def create_organization_context():
  key_name = random.choice([
    {"key": "org-7f9f58eb-c8e8-4c40-9962-43b13eeec4ea", "name": "Mayo Clinic", "employees": 76000}, 
    {"key": "org-40fad050-3f91-49dc-8007-33d02f1869e0", "name": "IBM", "employees": 288000}, 
    {"key": "org-fca878d0-3cab-4301-91da-bbc6dbb08fff", "name": "3M", "employees": 92000},
    {"key": "org-d4e7a912-b8f3-4b2c-9e15-df3c2f8e7b21", "name": "Microsoft", "employees": 221000},
    {"key": "org-a1b2c3d4-e5f6-4a3b-8c7d-9e0f1a2b3c4d", "name": "Google", "employees": 156000},
    {"key": "org-f7e6d5c4-b3a2-4d1e-9f8e-7d6c5b4a3f2e", "name": "Apple", "employees": 164000},
    {"key": "org-1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d", "name": "Amazon", "employees": 1608000},
    {"key": "org-9d8c7b6a-5f4e-3d2c-1b0a-9f8e7d6c5b4a", "name": "Meta", "employees": 66000},
    {"key": "org-5c4d3e2f-1a0b-9c8d-7e6f-5a4b3c2d1e0f", "name": "Netflix", "employees": 12800},
    {"key": "org-2d1e0f9a-8b7c-6d5e-4f3a-2b1c0d9e8f7a", "name": "Adobe", "employees": 29239},
    {"key": "org-7b6a5c4d-3e2f-1d0c-9b8a-7f6e5d4c3b2a", "name": "Salesforce", "employees": 70000},
    {"key": "org-e2f1d0c9-b8a7-6c5d-4e3f-2a1b0c9d8e7f", "name": "Intel", "employees": 131900},
    {"key": "org-8a7b6c5d-4e3f-2d1c-0b9a-8f7e6d5c4b3a", "name": "Cisco", "employees": 83300},
    ])
  region = random.choice(['NA', 'CN', 'EU', 'IN', 'SA'])

  org_context = Context.builder(key_name["key"]) \
  .set("kind", "organization") \
  .set("name", key_name["name"]) \
  .set("region", region) \
  .set("employees", key_name["employees"]) \
  .build()

  return org_context

'''
Construct a multi context: User, Device, and Organization
'''
def create_multi_context():

  multi_context = Context.create_multi(
  create_user_context(),
  create_device_context(),
  create_organization_context()
  )

  return multi_context