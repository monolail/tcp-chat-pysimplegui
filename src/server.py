import socket
import threading
import protocol

clients = []  # 접속한 클라이언트 소켓들을 저장할 리스트
chat_history = []  # 채팅 기록을 저장할 리스트

HOST = '127.0.0.1'  # 내 컴퓨터 주소 (localhost)
PORT = 9999         # 통신할 포트 번호


def handle_client(client_socket, addr):

    while True:
        try:
            # 클라이언트가 보낸 데이터를 최대 1024바이트 읽어서 문자열로 변환
            data = client_socket.recv(1024).decode('utf-8')
            # 연결이 끊겼거나 'exit'을 보냈으면 종료
            if not data or data == 'exit':
                print(f"[접속 종료] 클라이언트 {addr}가 나갔습니다.")
                break
            print(f"[받은 메시지] {data}")
            chat_history.append(data)  # 채팅 기록에 추가

            # 받은 메시지를 모든 클라이언트에게 전송
            for client in clients:
                if client != client_socket:  # 메시지를 보낸 클라이언트 제외
                    client.sendall(f"[{addr[1]}번 님응답] {data}".encode('utf-8'))

        except ConnectionResetError:
            print(f"[접속 종료] 클라이언트 {addr}와의 연결이 끊겼습니다.")
            break

    clients.remove(client_socket)  # 접속 종료된 클라이언트 소켓 제거
    client_socket.close()

def start_server():

    # 1. TCP 소켓(전화기) 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"[서버 시작] {HOST}:{PORT} 에서 클라이언트를 기다리는 중...")
    
    while True:

        client_socket, addr = server_socket.accept()  # 클라이언트 접속 대기
        clients.append(client_socket)  # 접속한 클라이언트 소켓을 리스트에 추가
        print(f"[접속 성공] 클라이언트가 연결되었습니다: {addr}")

        # 클라이언트와 통신할 스레드 생성 및 시작
        client_thread = threading.Thread(target=handle_client, args=(client_socket,addr),daemon=True)
        client_thread.start()



if __name__ == "__main__":
    start_server()