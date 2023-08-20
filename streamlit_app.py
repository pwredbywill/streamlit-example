import streamlit as st
import requests
import json

# Define your FedEx API credentials
CLIENT_ID = ""
CLIENT_SECRET = ""


# Function to obtain the bearer access token
def get_access_token():
    token_url = "https://apis.fedex.com/oauth/token"
    token_payload = "grant_type=client_credentials&client_id=" + CLIENT_ID + "&client_secret=" + CLIENT_SECRET
    token_header = {
        'Content-Type': "application/x-www-form-urlencoded"
    }
    token_response = requests.request("POST", token_url, data=token_payload, headers=token_header)

    if token_response.status_code == 200:
        token_data = token_response.json()
        bear_access_token = token_data["access_token"]
        return bear_access_token
    else:
        return None


# Streamlit app title
st.title("FedEx Shipping Cost Estimator")

shipper_zip = st.text_input("Shipper Zip Code")
destination_zip = st.text_input("Destination Zip Code")
length = st.number_input("Length (inches)")
width = st.number_input("Width (inches)")
height = st.number_input("Height (inches)")
weight = st.number_input("Weight (lbs)")
service_type = st.selectbox("Service Type",
                            ["GROUND_HOME_DELIVERY", "FEDEX_2_DAY", "FEDEX_2_DAY_AM", "FIRST_OVERNIGHT",
                             "FEDEX_EXPRESS_SAVER", "PRIORITY_OVERNIGHT", "STANDARD_OVERNIGHT"])

# Calculate shipping cost on button press
if st.button("Calculate Shipping Cost"):
    access_token = get_access_token()
    if access_token:
        url = "https://apis.fedex.com/rate/v1/rates/quotes"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token
        }
        payload = {
            "accountNumber": {
                "value": "632211163"
            },
            "requestedShipment": {
                "shipper": {
                    "address": {
                        "postalCode": shipper_zip,
                        "countryCode": "US"
                    }
                },
                "recipient": {
                    "address": {
                        "postalCode": destination_zip,
                        "countryCode": "US",
                        "residential": True
                    }
                },
                "serviceType": service_type,
                "pickupType": "USE_SCHEDULED_PICKUP",
                "rateRequestType": [
                    "ACCOUNT",
                    "LIST"
                ],
                "requestedPackageLineItems": [
                    {
                        "subPackagingType": "BOX",
                        "groupPackageCount": 1,
                        "weight": {
                            "units": "LB",
                            "value": weight
                        },
                        "dimensions": {
                            "length": length,
                            "width": width,
                            "height": height,
                            "units": "IN"
                        },
                        "variableHandlingChargeDetail": {
                            "rateType": "ACCOUNT",
                            "percentValue": 0,
                            "rateLevelType": "INDIVIDUAL_PACKAGE_RATE",
                            "rateElementBasis": "NET_CHARGE"
                        }
                    }
                ]
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            for item in response_json["output"]["rateReplyDetails"]:
                st.write("Total Base Charge:", item["ratedShipmentDetails"][0]["totalBaseCharge"])
                st.write("Total Surcharges:", item["ratedShipmentDetails"][0]["shipmentRateDetail"]["totalSurcharges"])
                st.write("Total Freight Discount:",
                         item["ratedShipmentDetails"][0]["shipmentRateDetail"]["totalFreightDiscount"])
                st.write("Total Net Charge:", item["ratedShipmentDetails"][0]["totalNetCharge"])
                st.write("-" * 30)
        else:
            st.error("Error occurred while calculating shipping cost.")
    else:
        st.error("Failed to obtain access token.")

