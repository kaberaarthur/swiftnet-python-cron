from sms import send_sms

response = send_sms("Hello System User your subscription has Expired. Visit https://swiftnet-fe.vercel.app/authentication/acustomer?id=225 to renew your subscription.", ['0790485731'])

print(response)
