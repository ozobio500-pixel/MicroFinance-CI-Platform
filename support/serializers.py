from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    sender_role = serializers.CharField(source="sender.role", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "sender", "sender_name", "sender_role", "content", "created_at")
        read_only_fields = ("id", "sender", "created_at")


class ConversationSerializer(serializers.ModelSerializer):
    client_detail = UserSerializer(source="client", read_only=True)
    assigned_agent_detail = UserSerializer(source="assigned_agent", read_only=True)
    client_username = serializers.CharField(source="client.username", read_only=True)
    assigned_agent_username = serializers.CharField(source="assigned_agent.username", read_only=True, allow_null=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = (
            "id",
            "client",
            "client_username",
            "client_detail",
            "assigned_agent",
            "assigned_agent_username",
            "assigned_agent_detail",
            "status",
            "subject",
            "messages",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "client", "assigned_agent", "status", "created_at", "updated_at")


class ConversationCreateSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Conversation
        fields = ("subject", "client", "client_username")
        extra_kwargs = {
            "client": {"required": False, "allow_null": True}
        }

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        if user.is_client:
            attrs["client"] = user
        else:
            client = attrs.get("client")
            client_username = attrs.get("client_username")
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if client_username:
                try:
                    client_user = User.objects.get(username=client_username, role=User.Role.CLIENT)
                    attrs["client"] = client_user
                except User.DoesNotExist:
                    raise serializers.ValidationError({"client_username": f"Le client '{client_username}' n'existe pas."})
            elif client:
                if not client.is_client:
                    raise serializers.ValidationError({"client": "L'utilisateur sélectionné doit être un client."})
            else:
                raise serializers.ValidationError({"client_username": "Un agent doit spécifier le client_username ou le client."})
        
        attrs.pop("client_username", None)
        return attrs
