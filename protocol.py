import json
import struct  # 숫자를 정확히 4바이트로 변환해주는 파이썬 기본 모듈

# 1. 택배 보내기 함수
def send_json(sock, data_dict):
    # (1) 파이썬 딕셔너리(data_dict)를 JSON 문자열로 바꾸고 utf-8 바이트로 인코딩
    json_bytes = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
    
    # (2) 데이터의 길이(바이트 수)를 4바이트 숫자('>I': 빅엔디안 4바이트 정수)로 포장
    header = struct.pack('>I', len(json_bytes))
    
    # (3) [4바이트 길이 헤더] + [JSON 본문]을 합쳐서 전송!
    sock.sendall(header + json_bytes)


# 2. 택배 받기 함수
def recv_json(sock):
    # (1) 먼저 앞의 4바이트(길이 표지판)를 읽음
    header = recv_exact(sock, 4)
    if not header:
        return None  # 상대방이 연결을 끊었으면 None 반환
        
    # (2) 4바이트 표지판을 해석해서 본문이 몇 바이트인지 숫자로 꺼냄
    msg_length = struct.unpack('>I', header)[0]
    
    # (3) 본문 길이(msg_length)만큼 정확히 데이터를 읽어서 딕셔너리로 복원!
    json_bytes = recv_exact(sock, msg_length)
    if not json_bytes:
        return None
        
    return json.loads(json_bytes.decode('utf-8'))


# [보조 함수] 소켓에서 정확히 n바이트가 다 모일 때까지 읽는 함수
def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data