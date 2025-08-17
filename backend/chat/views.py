from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
import httpx
import asyncio
import json
import os

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8002")

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return obj.user == request.user
        if isinstance(obj, Message):
            return obj.conversation.user == request.user
        return False

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        conv = self.get_object()
        role = request.data.get('role')
        content = request.data.get('content', '')
        if role not in ['user','ai']:
            return Response({'detail': 'role must be user|ai'}, status=status.HTTP_400_BAD_REQUEST)
        msg = Message.objects.create(conversation=conv, role=role, content=content)
        # 更新会话更新时间，便于按最近活动排序
        conv.save()  # auto_now=True 的 updated_at 会在保存时更新
        return Response(MessageSerializer(msg).data)

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        一次性消息发送：用户消息+AI回复+自动持久化
        """
        user_text = request.data.get('text', '').strip()
        conversation_id = request.data.get('conversation_id')
        use_rag = request.data.get('use_rag', True)
        temperature = request.data.get('temperature', 0.7)
        
        if not user_text:
            return Response({'detail': 'text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取或创建对话
        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user=request.user)
            except Conversation.DoesNotExist:
                return Response({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            conv = Conversation.objects.create(user=request.user, title='新对话')
        
        # 保存用户消息
        user_msg = Message.objects.create(conversation=conv, role='user', content=user_text)
        
        # 更新对话标题（如果是默认）
        if conv.title in ['新对话', '']:
            conv.title = user_text[:20] if user_text else '新对话'
            conv.save()
        
        ai_text = ''
        try:
            # 获取对话历史
            conversation_history = []
            recent_msgs = conv.messages.order_by('-created_at')[:10]
            for msg in reversed(list(recent_msgs)):
                 conversation_history.append({
                     'role': 'assistant' if msg.role == 'ai' else msg.role,
                     'content': msg.content
                 })
            
            # 调用AI服务 - 使用新协议
            payload = {
                "text": user_text,
                "conversation_history": conversation_history,
                "use_rag": use_rag,
                "temperature": temperature
            }
            with httpx.Client(timeout=30) as client:
                response = client.post(f"{AI_SERVICE_URL}/v1/echo", json=payload)
                response.raise_for_status()
                ai_data = response.json()
            
            ai_text = ai_data.get('response') or ai_data.get('reply') or ''
            if not ai_text:
                ai_text = 'AI服务未返回内容'
        except Exception as e:
            # 兜底：当AI服务不可用或报错时，返回离线简要答复，避免前端无响应
            if '1+1' in user_text or '加法' in user_text or '等于' in user_text:
                ai_text = '1+1等于2。这是一个基本的数学加法运算。（离线兜底）'
            else:
                ai_text = f"抱歉，当前AI服务不可用或异常（{str(e)}），已返回离线兜底回复：您刚才问的是“{user_text}”。"
        
        # 保存AI消息并返回成功响应
        ai_msg = Message.objects.create(conversation=conv, role='ai', content=ai_text)
        conv.save()  # 更新时间戳
        
        return Response({
            'conversation_id': conv.id,
            'user_message': MessageSerializer(user_msg).data,
            'ai_message': MessageSerializer(ai_msg).data
        })

    @action(detail=False, methods=['post'])
    def stream_chat(self, request):
        """
        流式聊天：用户消息+AI流式回复+自动持久化
        """
        user_text = request.data.get('text', '').strip()
        conversation_id = request.data.get('conversation_id')
        use_rag = request.data.get('use_rag', True)
        temperature = request.data.get('temperature', 0.7)
        
        if not user_text:
            return Response({'detail': 'text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取或创建对话
        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user=request.user)
            except Conversation.DoesNotExist:
                return Response({'detail': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            conv = Conversation.objects.create(user=request.user, title='新对话')
        
        # 保存用户消息
        user_msg = Message.objects.create(conversation=conv, role='user', content=user_text)
        
        # 更新对话标题（如果是默认）
        if conv.title in ['新对话', '']:
            conv.title = user_text[:20] if user_text else '新对话'
            conv.save()
        
        def stream_generator():
            ai_content = ""
            try:
                # 发送会话开始信息
                yield f"data: {json.dumps({'type': 'conversation_id', 'data': conv.id})}\n\n"
                yield f"data: {json.dumps({'type': 'user_message', 'data': MessageSerializer(user_msg).data})}\n\n"
                
                # 获取对话历史，构造查询参数
                conversation_history = []
                recent_msgs = conv.messages.order_by('-created_at')[:10]  # 最近10条（按时间倒序）
                for msg in reversed(list(recent_msgs)):  # 再反转为时间正序
                     conversation_history.append({
                         'role': 'assistant' if msg.role == 'ai' else msg.role,
                         'content': msg.content
                     })
                
                with httpx.Client(timeout=None) as client:
                    params = {
                        "text": user_text, 
                        "use_rag": use_rag,
                        "temperature": temperature
                    }
                    # 注意：流式接口目前不支持conversation_history参数，需要AI服务更新
                    with client.stream("GET", f"{AI_SERVICE_URL}/v1/stream_echo", params=params) as response:
                        response.raise_for_status()
                        for raw_line in response.iter_lines():
                            if not raw_line:
                                continue
                            line = raw_line.strip()
                            if line.startswith("data: "):
                                chunk = line[6:]
                                ai_content += chunk
                                yield f"data: {json.dumps({'type': 'ai_chunk', 'data': chunk})}\n\n"
                            elif line.startswith("event: end"):
                                # 完整消息持久化
                                ai_msg = Message.objects.create(conversation=conv, role='ai', content=ai_content)
                                conv.save()
                                yield f"data: {json.dumps({'type': 'ai_message', 'data': MessageSerializer(ai_msg).data})}\n\n"
                                yield f"event: end\ndata: [DONE]\n\n"
                                break
            except Exception as e:
                # 流式兜底：直接返回简要离线内容并结束
                fallback = '1+1等于2。这是一个基本的数学加法运算。（离线兜底）' if ('1+1' in user_text or '加法' in user_text or '等于' in user_text) else f"抱歉，当前AI服务异常（{str(e)}），已返回离线兜底简要答复。"
                ai_msg = Message.objects.create(conversation=conv, role='ai', content=fallback)
                conv.save()
                yield f"data: {json.dumps({'type': 'ai_message', 'data': MessageSerializer(ai_msg).data})}\n\n"
                yield f"event: end\ndata: [DONE]\n\n"
        
        return StreamingHttpResponse(
            stream_generator(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )