import json
# convert a json to string with the backslash and stuff 

data = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action" : "ds:Delete*",
            "Resource": "*"
        }
    ],
}

# print the string form of data like if it's in a string 
val = {
    "data" : f"{data}"
}

print(val)
