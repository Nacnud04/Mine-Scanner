def startGui():
    import PySimpleGUI as sg
    waiting = True
    sg.theme('DarkAmber')

    layout = [  [sg.Text('Cave Reader')],
                [sg.Button('Shot'), sg.Button('Passage')],
                [sg.Button('Room'), sg.Button('Formation')],
                [sg.Text('X: '), sg.Text(size=(15,1), key='-x-'), sg.Text('ft')],
                [sg.Text('Y: '), sg.Text(size=(15,1), key='-y-'), sg.Text('ft')],
                [sg.Text('Z: '), sg.Text(size=(15,1), key='-z-'), sg.Text('ft')],
                [sg.Text('Station: '), sg.Text(size=(15,1), key='-station-')]]

    window = sg.Window('Cave Reader Window', layout)

    while waiting == True :
        event, values = window.read()
        print(event, values)
        if event != "":
            waiting = False
            print('Event')
            waiting = True
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
