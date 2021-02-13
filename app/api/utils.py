def mask_email(email):
  address, domain = email.split("@")
  mask_length = 1 if len(address) <= 6 else 3
  new_email = address[:mask_length] + "****" + address[len(address)-mask_length:] + "@" + domain
  return new_email
