from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.serializers import TokenVerifySerializer

class TokenVerifyWithUserIdSerializer(TokenVerifySerializer):
    """
    Inherit the normal verify serializer but also return the user_id
    that’s embedded in the access token’s payload.
    """
    def validate(self, attrs):
        data = super().validate(attrs)      # raises if token is bad/expired
        data["user_id"] = self.token.payload.get("user_id")
        return data


class TokenVerifyWithUserIdView(TokenVerifyView):
    """
    POST { "token": "<access>" }  →  { "token": "<access>", "user_id": 3 }
    """
    serializer_class = TokenVerifyWithUserIdSerializer