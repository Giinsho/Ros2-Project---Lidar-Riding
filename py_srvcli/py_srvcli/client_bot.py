import subprocess
import os


def main():
    while True:
        os.system("clear")
        print(("--ROBOT--LOCATION--"))
        print("\nChoose place you want to be : ")
        print("""
        1 : Kanciapa
        2 : Sypialnia
        3 : Kuchnia
        4 : Korytarz
        5 : Goscinny
        6 : Przedsionek
        7 : Wyjscie
        8 : Własne współrzędne
        0 : Exit from program"""
              )
        choice = input("\nEnter your choice : ")

        if choice == '1':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: kanciapa}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '2':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: sypialnia}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '3':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: kuchnia}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '4':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: korytarz}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '5':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: goscinny}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '6':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: przedsionek}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '7':
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: wyjscie}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '8':
            x = input("Podaj x: ")
            y = input("Podaj y: ")
            bashCommand = 'source install/setup.bash && ros2 action send_goal move action_bot/action/Move "{request: x:'+str(
                x)+','+'y:'+str(y)+'}"'
            output = subprocess.check_output(['bash', '-c', bashCommand])
        elif choice == '0':
            exit()
        os.system("clear")


if __name__ == "__main__":
    main()
