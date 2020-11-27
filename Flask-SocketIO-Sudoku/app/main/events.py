import json
from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from sudoku import Sudoku
from random import shuffle, seed as random_seed, randrange
import sys
people = {}
people_names = [] 
values = {}
states = {}

@socketio.on('joined', namespace='/chat')
def joined(message):
    global people, people_names
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    name = session.get('name')    
    while name in people:
        name = name + '1'
    if name not in people_names:
        people_names.append(name)
    people[name] = 0
    ids = people_names.index(name)
    if values:
        print('values sent')
        emit('answer', json.dumps(values), room=room)
        emit('question', json.dumps(states), room=room)
    emit('status', {'msg': name + ' with id ' + str(ids) + ' has entered the room.', 'id': ids}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    global people_names, people, states
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    name = people_names[message['a0']]
    score_id = people_names.index(name)
    people[name] += 1
    states[message['a1']] = 1
    emit('question', json.dumps(states), room=room)
    emit('status', {'msg': name + ' has got ' + message['a1'] + ' cell.', 'id': score_id}, room=room)

@socketio.on('solve', namespace='/chat')
def solve():
    global states
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    for key in states:
        states[key] = 1
    emit('question', json.dumps(states), room=room)

@socketio.on('test', namespace='/chat')
def test(message):
    global people_names, people, values, states
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    print(message['level'])
    level = float(message['level'])/10.0
    puzzle = Sudoku(3,seed=randrange(sys.maxsize)).difficulty(level)
    board = puzzle.board
    solution = puzzle.solve().board
    print(solution)
    matring(solution, board)
    emit('answer', json.dumps(values), room=room)
    emit('question', json.dumps(states), room=room)
    if people:
        leader = max(people, key=people.get)
        lead_id = people_names.index(leader)
        emit('status', {'msg': leader + ' with id ' + str(lead_id) + ' is the leader with ' + str(people[leader]) + ' points.', 'id': lead_id}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    global people, people_names, control_id
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    ids = message['id']
    name = people_names[ids]
    score = people[name]
    people.pop(name)
    emit('status', {'msg': name + ' and id' + str(ids) + ' has left the room with a score of' + str(score), 'id': ids}, room=room)

def matring(solution, board):
    global values, states 
    i = 0
    while i < 9:
        j = 0
        while j < 9: 
            cell = "a"+str(i+1)+str(j+1)        
            values[cell] = solution[i][j]
            if board[i][j] is not None:
                states[cell] = 1
            else:
                states[cell] = 0
            j += 1
        i += 1
