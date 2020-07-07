

def prompt_yes_no_question(yes_responses=("y", "yes"),
                           no_responses=("n", "no"),
                           case_sensitive=False,
                           default_yes_response=True):

    prompt_message = "Do you want to continue? (Y/n): "
    if not default_yes_response:
        prompt_message = "Do you want to continue? (y/N): "

    check = str(input(prompt_message)).strip()
    if not case_sensitive:
        check = check.lower()

    try:
        if check == "":
            return default_yes_response
        if check in yes_responses:
            return True
        elif check in no_responses:
            return False
        else:
            print('Invalid input. Please try again.')
            return prompt_yes_no_question(yes_responses, no_responses,
                                          case_sensitive, default_yes_response)
    except Exception as e:
        print("Exception occurred: {}. Please enter valid inputs.".format(e))
        return prompt_yes_no_question(yes_responses, no_responses,
                                      case_sensitive, default_yes_response)
