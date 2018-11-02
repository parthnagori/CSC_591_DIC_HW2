import os
import sys
import argparse
from itertools import cycle

# def is_id_in_range(start, end, val):
#   print("is {} in [{},{}]".format(val,start,end))
#   offset = (ring_length - start)%ring_length
#   start = (start+offset)%ring_length
#   end = (end+offset)%ring_length
#   val = (val+offset)%ring_length
#   print(start <= val <= end)
#   return start <= val <= end

def is_id_in_range(start,end,val):
  start = start%ring_length
  end = end%ring_length
  if start <= end:
    node_range = [i for i in range(start,end)]
    return val in node_range
  else:
    node_range = set([i for i in range(0,end)] + [i for i in range(start,ring_length)])
    return val in node_range

def get_start(val, i):
  return ( (val + (2**i)) % (2**m) )

class Node:
  def __init__(self,val):
    self.id = val
    self.predecessor = self
    self.finger = [self for i in range(m)]

  def join(self, n1):
    print("Inside join")
    self.init_finger_table(n1)
    self.update_others()
    
  def init_finger_table(self, n1):
    # print("init finger")
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

  def find_predecessor(self,val):
    # print("find pre")
    n1 = self
    temp_val = n1.id
    while not is_id_in_range(n1.id+1,n1.finger[0].id+1,val):
      n1 = n1.closest_preceding_finger(val)
      if n1.id == temp_val:
        break
      temp_val = n1.id
    return n1

  def update_finger_table(self, s, i):
    # print("Updating finger table : {} --- {}".format(s,i))
    if (is_id_in_range(self.id, self.finger[i].id, s.id)):
      self.finger[i] = s
      p = self.predecessor
      # print("{} pred : {}".format(self.id, p))
      p.update_finger_table(s,i)

  def update_others(self):
    # print("update others")
    for i in range(0,m):
      p = self.find_predecessor((self.id - (2**i))%(2**m))
      # print("P : {}".format(p))
      p.update_finger_table(self, i)

  def stabilize(self):
    # print("Inside stabilize")
    if self.predecessor and self.predecessor.id not in ring:
      self.predecessor = self
    if self.finger[0] and self.finger[0].id not in ring:
      self.finger[0] = self

    x = self.finger[0].predecessor
    if is_id_in_range(self.id+1, self.finger[0].id, x.id):
      # print(x)
      self.finger[0] = x
    self.finger[0].notify(self)

  def notify(self, n1):
    # print("Inside notify for n - {} and n1 - {}".format(self.id, n1.id))
    if not self.predecessor or (is_id_in_range(self.predecessor.id+1, self.id, n1.id)):
      self.predecessor = n1

  def fix_fingers(self):
    # print("Inside Fix Fingers")
    for i in range(0,m):
      curr_finger_start = get_start(self.id, i)
      self.finger[i] = self.find_successor(curr_finger_start)

  def display(self):
    succ = self.finger[0].id if self.finger[0] else None
    pred = self.predecessor.id if self.predecessor else None
    finger_table = ",".join(str(x.id) for x in self.finger)
    print("< Node {}: suc {}, pre {}: finger {}".format(self.id, succ, pred, finger_table))

  def find_successor(self, val):
    # print("Find successor {}".format(val))
    n1 = self.find_predecessor(val)
    return n1.finger[0]
    # if (is_id_in_range(self.id+1, self.finger[0].id, val)):
    #   return self.finger[0]
    # else:
    #   n0 = self.closest_preceding_finger(val)
    #   return n0.find_successor(val)

  def closest_preceding_finger(self, val):
    for i in range(m-1,-1,-1):
      curr_finger_id = self.finger[i].id
      if is_id_in_range(self.id+1, val, curr_finger_id):
        return self.finger[i]
    return self


def execute(method, value=None, value1=None):
  if method == "add" and value != None:
    if value in ring:
      print("Node {} exists".format(value))
    else:    
      node = Node(value)
      ring[value] = node
      # print("Added node {}".format(value))
  
  elif method == "join" and value != None and value1 != None:
    n = ring[value]
    n1 = ring[value1]
    n.join(n1)
  
  elif method == "drop":
    # print("Inside Drop")
    for k,node in ring.items():
      for i in range(m):
        if node.finger[i].id == ring[value].id:
          node.finger[i] = node
    ring.pop(value)

  elif method == "fix" and value != None:
    # print("Inside Fix")
    if value in ring:
      node = ring[value]
      node.fix_fingers()
    else:
      print("Node {} does not exist".format(value))
  
  elif method == "stab" and value != None:
    # print("Inside Stab")
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


def parse_and_execute(instruction, m):
  operands = instruction.split(" ")
  # print(operands)
  
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


def execute_file_instructions(filename, m):
  with open(filename) as f:
    for line in f:
      print("> {}".format(line.strip()))
      parse_and_execute(line.strip(),m)

if __name__ == '__main__':
  m = 0
  ring_length = 0
  ring = {}
  args = sys.argv
  # print(args)
  if len(args) == 4:
    test_file = args[2]
    m = int(args[3])
    ring_length = int(2**m)
    execute_file_instructions(test_file, m)
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

