from ui_manager import show_menu


def main():
    while True:
        choice = show_menu()

        if choice == "1":
            print("Add inventory.")

        elif choice == "2":
            print("View inventory.")

        elif choice == "3":
            print("AI analysis.")

        elif choice == "4":
            print("Zhaos!")
            break

        else:
            print("Please enter 1, 2, 3 or 4.")


    main()