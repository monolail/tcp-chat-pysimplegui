import socket
import threading
import FreeSimpleGUI as sg  # (만약 정품 PySimpleGUI 키를 발급받으셨다면 import PySimpleGUI as sg 로 쓰시면 됩니다)

HOST = '127.0.0.1'
PORT = 9999

# 1. [듣기 전용 분신 스레드] 서버에서 오는 메시지를 받아서 GUI 창으로 전달!
def receive_messages(client_socket, window):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            # 백그라운드 스레드에서 GUI 창에 안전하게 메시지를 전달하는 신호 보내기
            window.write_event_value('-RECV-', data)
        except:
            break
    window.write_event_value('-DISCONNECTED-', '서버와의 연결이 종료되었습니다.')


def main():
    sg.theme('DarkBlue3')  # 깔끔한 테마 색상 설정

    # 2. [GUI 화면 디자인] 위에서 아래로 한 줄씩 배치됩니다
    layout = [
        [sg.Text(f'서버 주소: {HOST}:{PORT}', size=(25, 1)), 
         sg.Text('상태: 연결 안 됨', key='-STATUS-', text_color='yellow')],
        
        # 채팅 내역이 출력될 큰 창
        [sg.Multiline(size=(50, 20), key='-CHATBOX-', disabled=True, autoscroll=True)],
        
        # 메시지 입력창 + 전송(SEND) 버튼 (엔터키를 눌러도 전송됨)
        [sg.Input(size=(40, 1), key='-INPUT-', do_not_clear=False), 
         sg.Button('SEND', bind_return_key=True, disabled=True)],
        
        # 접속 / 접속 해제 / 종료 버튼
        [sg.Button('CONNECT', size=(12, 1)), 
         sg.Button('DISCONNECT', size=(12, 1), disabled=True), 
         sg.Button('EXIT', size=(12, 1))]
    ]

    window = sg.Window('나만의 TCP 채팅 클라이언트', layout, font=('맑은 고딕', 11))
    client_socket = None
    is_connected = False

    # 3. [GUI 이벤트 루프] 버튼 클릭 처리
    while True:
        event, values = window.read()

        # 창 닫기(X)나 EXIT 버튼을 누른 경우
        if event in (sg.WIN_CLOSED, 'EXIT'):
            if is_connected and client_socket:
                client_socket.sendall('exit'.encode('utf-8'))
                client_socket.close()
            break

        # [CONNECT 버튼] 서버에 접속하기
        elif event == 'CONNECT' and not is_connected:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # TODO 1: 서버 (HOST, PORT)로 연결(connect)하세요 (1줄)
                client_socket.connect((HOST, PORT))
                
                my_ip, my_port = client_socket.getsockname()
                is_connected = True

                # 듣기 전용 스레드 시작!
                threading.Thread(target=receive_messages, args=(client_socket, window), daemon=True).start()

                # UI 상태 업데이트
                window['-STATUS-'].update(f'상태: 접속됨 (내 포트: {my_port})', text_color='lightgreen')
                window['-CHATBOX-'].print(f'[안내] 서버에 접속했습니다! (내 번호: {my_port})')
                window['CONNECT'].update(disabled=True)
                window['DISCONNECT'].update(disabled=False)
                window['SEND'].update(disabled=False)

            except Exception as e:
                window['-CHATBOX-'].print(f'[오류] 서버 연결 실패: {e}')

        # [SEND 버튼] 메시지 보내기
        elif event == 'SEND' and is_connected:
            msg = values['-INPUT-'].strip()
            if msg:
                # TODO 2: 입력한 msg를 utf-8로 인코딩해서 서버에 전송(sendall)하세요 (1줄)
                client_socket.sendall(msg.encode('utf-8'))
                
                # 내 채팅창에도 내가 보낸 말 표시하기
                window['-CHATBOX-'].print(f'[나] {msg}')

        # [DISCONNECT 버튼] 접속 끊기
        elif event == 'DISCONNECT' and is_connected:
            client_socket.sendall('exit'.encode('utf-8'))
            client_socket.close()
            is_connected = False
            window['-STATUS-'].update('상태: 연결 해제됨', text_color='yellow')
            window['-CHATBOX-'].print('[안내] 채팅방에서 나왔습니다.')
            window['CONNECT'].update(disabled=False)
            window['DISCONNECT'].update(disabled=True)
            window['SEND'].update(disabled=True)

        # [서버로부터 메시지가 도착했을 때]
        elif event == '-RECV-':
            recv_msg = values['-RECV-']
            window['-CHATBOX-'].print(recv_msg)

    window.close()

if __name__ == "__main__":
    main()