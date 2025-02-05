import plivo
from plivo.utils.template import Template
from django.conf import settings  

client = plivo.RestClient(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)

# template=Template(**{ 
#             "name": "template_name",
#             "language": "en_US",
#             "components": [
#                 {
#                     "type": "header",
#                     "parameters": [
#                         {
#                             "type": "media",
#                             "media": "https://xyz.com/s3/img.jpg"
#                         }
#                     ]
#                 },
#                 {
#                     "type": "body",
#                     "parameters": [
#                         {
#                             "type": "text",
#                             "text": "WA-Text"
#                         }
#                     ]
#                 }
#             ]
#           }
#        )
# response = client.messages.create(   
#         src="8310557717",
#         dst="+917463906582",
#         type_="whatsapp",
#         template=template,
#         url="https://foo.com/wa_status/"
#     )
# print(response)

# response = client.messages.create(
#          src="+918310557717",
#          dst="+917463906582",
#          type_="whatsapp",
#          text="whatsapp_video",
#          media_urls=["https://sample-videos.com/img/Sample-png-image-1mb.png"]
#         )
# print(response)