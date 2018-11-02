###########################
## Author: Parth Nagori  ##
## Unity ID: pnagori     ##
## Student ID: 200208747 ##
###########################

import os
import sys
import argparse
from itertools import cycle

#if value lies in given range of [start,end)
def is_id_in_range(start,end,val):
  start = start%ring_length
  end = end%ring_length
  if start <= end:
    node_range = [i for i in range(start,end)]
    return val in node_range
  else:
    node_range = set([i for i in range(0,end)] + [i for i in range(start,ring_length)])
    return val in node_range

#get start value for a finger table entry
def get_start(val, i):
  return ( (val + (2**i)) % (2**m) )

#Class Node to store an entry in the network
class Node:
  #Node constructor
  def __init__(self,val):
    self.id = val
    self.predecessor = self
    self.finger = [self for i in range(m)]

  #Joining node self to n1
  def join(self, n1):
    self.init_finger_table(n1)
    self.update_others()

  #Initializing finger table of node upon joining node to n1  
  def init_finger_table(self, n1):
    finger_start = get_start(self.finger[0].id, 0)
    self.finger[0] = n1.find_successor(finger_start)
    self.predecessor = self.finger[0].predecessor
    self.finger[0].predecessor = self
    for i in range(0,m-1):
      curr_finger_start = get_start(self.finger[i+1].id, i+1)
      if is_id_in_range(self.id, self.finger[i].id, curr_finger_start):
        self.finger[i+1] = self.finger[i]
      else:
        self.finger[i+1] = n1.find_successor(curr_finger_start)

  #Finding predecessor of current node
  def find_predecessor(self,val):
    n1 = self
    temp_val = n1.id
    while not is_id_in_range(n1.id+1,n1.finger[0].id+1,val):
      n1 = n1.closest_preceding_finger(val)
      if n1.id == temp_val:
        break
      temp_val = n1.id
    return n1

  #Updating finger table upon joining node to n1
  def update_finger_table(self, s, i):
    if (is_id_in_range(self.id, self.finger[i].id, s.id)):
      self.finger[i] = s
      p = self.predecessor
      p.update_finger_table(s,i)

  #Update others getting called after initializing finger table
  def update_others(self):
    for i in range(0,m):
      p = self.find_predecessor((self.id - (2**i))%(2**m))
      p.update_finger_table(self, i)

  #Verifying node’s immediate successor and telling the successor about node
  def stabilize(self):
    if self.predecessor and self.predecessor.id not in ring:
      self.predecessor = self
    if self.finger[0] and self.finger[0].id not in ring:
      self.finger[0] = self

    x = self.finger[0].predecessor
    if is_id_in_range(self.id+1, self.finger[0].id, x.id):
      self.finger[0] = x
    self.finger[0].notify(self)

  #n1 thinks it might be our predecessor
  def notify(self, n1):
    if not self.predecessor or (is_id_in_range(self.predecessor.id+1, self.id, n1.id)):
      self.predecessor = n1

  #Fixing finger table of the current node
  def fix_fingers(self):
    for i in range(0,m):
      curr_finger_start = get_start(self.id, i)
      self.finger[i] = self.find_successor(curr_finger_start)

  #Display a single node's contents
  def display(self):
    succ = self.finger[0].id if self.finger[0] else None
    pred = self.predecessor.id if self.predecessor else None
    finger_table = ",".join(str(x.id) for x in self.finger)
    print("< Node {}: suc {}, pre {}: finger {}".format(self.id, succ, pred, finger_table))

  #Finding current node's successor 
  def find_successor(self, val):
    n1 = self.find_predecessor(val)
    return n1.finger[0]

  #Return closest finger preceding val 
  def closest_preceding_finger(self, val):
    for i in range(m-1,-1,-1):
      curr_finger_id = self.finger[i].id
      if is_id_in_range(self.id+1, val, curr_finger_id):
        return self.finger[i]
    return self


#Method to execute a command
def execute(method, value=None, value1=None):
  if method == "add" and value != None:
    if value in ring:
      print("Node {} exists".format(value))
    else:    
      node = Node(value)
      ring[value] = node
  
  elif method == "join" and value != None and value1 != None:
    if value in ring and value1 in ring:
      n = ring[value]
      n1 = ring[value1]
      n.join(n1)
    else:
      print("Node does not exist")
  
  elif method == "drop" and value != None:
    if value in ring:
      for k,node in ring.items():
        for i in range(m):
          if node.finger[i].id == ring[value].id:
            node.finger[i] = node
      ring.pop(value)
    else:
      print("Node does not exist")

  elif method == "fix" and value != None:
    if value in ring:
      node = ring[value]
      node.fix_fingers()
    else:
      print("Node {} does not exist".format(value))
  
  elif method == "stab" and value != None:
    if value in ring:
      node = ring[value]
      node.stabilize()
    else:
      print("Node {} doesn't exist".format(value))
  elif method == "show" and value != None:
    if value in ring:
      node = ring[value]
      node.display()
    else:
      print("Node {} does not exist".format(value))
  
  elif method == "list":
    for key, node in ring.items():
      node.display()

  elif method == "end":
    return "end"
  
  else:
    print("Invalid input")

#Parsing an instruction from input
def parse_and_execute(instruction, m):
  operands = instruction.split(" ")
  if len(operands) == 3:
    method = operands[0].lower()
    try:
      value1 = int(operands[1])
      value2 = int(operands[2])
      if value1 > (2**m - 1) or value2 > (2**m -1):
        return "invalid"
    except ValueError:
      return "invalid"
    return execute(method, value1, value2)
  
  elif len(operands) == 2:
    method = operands[0].lower()
    try:
      value = int(operands[1])
      if value > (2**m -1):
        return "invalid"
    except ValueError:
      return "invalid"
    return execute(method, value)
  
  elif len(operands) == 1:
    method = operands[0].lower()
    return execute(method)
  
  else:
    return "invalid"

#Reading instructions from the file
def execute_file_instructions(filename, m):
  with open(filename) as f:
    for line in f:
      print("> {}".format(line.strip()))
      parse_and_execute(line.strip(),m)

#Main
if __name__ == '__main__':
  m = 0
  ring_length = 0
  ring = {}
  args = sys.argv
  #If reading from file
  if len(args) == 4:
    test_file = args[2]
    m = int(args[3])
    ring_length = int(2**m)
    execute_file_instructions(test_file, m)
  #
  elif len(args) == 2:
    m = int(args[1])
    ring_length = int(2**m)
    while(True):
      print("\n>",end='')
      instruction = input()
      flag = parse_and_execute(instruction, m)
      if flag == "end":
        break
      elif flag == "invalid":
        print("Invalid input")
  else:
    print("\nInvalid number of arguments")

