import pickle

x = {}
x['username'] = input()
x['password'] = input()
x['client_id'] = '54af9fd3-db99-4efa-a14c-159279b3d5b2'
x['tenant_id'] = 'ec09e4d7-3d0f-4eff-9c1e-7ba8060c5417'

with open('credentials.dict', 'wb')as f:
    pickle.dump(x, f)