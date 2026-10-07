import ui_manager

def main():
    ui_manager.print_header()

    while True:
        choice = ui_manager.get_main_menu_choice()

        if choice == "1":
            print("Add inventory.")
            
        elif choice == "2":
            print("View inventory.")

        elif choice == "3":
            print("AI analysis.")

        elif choice == "4":
            print("View previous procurement recommendations.")
            break

        elif choice == "5":
            print("Exiting application.")
            break

        else:
            print("Please enter 1, 2, 3, 4 or 5.")

if __name__ == "__main__":
    main()
