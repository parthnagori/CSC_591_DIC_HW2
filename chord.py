import os
import sys
import argparse
from itertools import cycle

def is_id_in_range(start, end, val, left, right):
  offset = (ring_length - start)%ring_length
  start = (start+offset)%ring_length
  end = (end+offset)%ring_length
  val = (val+offset)%ring_length
  if left and right:
    return start <= val <= end
  elif left:
    return start <= val < end
  elif right:
    return start < val <= end
  else:
    return start < val < end

def get_start(val, i):
  return (val + (2**i))

class Node:
  def __init__(self,val):
    self.id = val
    self.predecessor = None
    # self.finger[0] = self
    self.finger = [self for i in range(m)]

  def join(self, n1):
    print("Inside join")
    self.predecessor = None
    self.finger[0] = n1.find_successor(self.id);
    self.stabilize()
    n1.stabilize()
    # self.init_finger_table(n1)
    # self.update_others()
    
  def init_finger_table(self, n1):
    finger_start = get_start(self.finger[0].id, 0)
    self.finger[0] = n1.find_successor(finger_start)
    self.predecessor = self.finger[0].predecessor
    self.finger[0].predecessor = self
    for i in range(0,m-1):
      curr_finger_start = get_start(self.finger[i+1].id, i+1)
      if is_id_in_range(self.id, self.finger[i].id, curr_finger_start, True, False):
        self.finger[i+1] = self.finger[i]
      else:
        self.finger[i+1] = n1.find_successor(curr_finger_start)

  # def update_others(self):
  #   for i in range(0,m):
  #     p = self.find_predecessor()

  def stabilize(self):
    print("Inside stabilize")
    x = self.finger[0].predecessor
    if x and is_id_in_range(self.id, self.finger[0].id, x.id, False, False):
      self.finger[0] = x
    self.finger[0].notify(self)
    # stabilize -- called periodically; node updates who it thinks its successor is.

  def notify(self, n1):
    print("Inside notify")
    if self.predecessor == None or (self.predecessor and is_id_in_range(self.predecessor.id, self.id, n1.id, False, False)):
      self.predecessor = n1
    # notify -- a node tells its successor that it exists so the successor can update it predecessor value.

  def fix_fingers(self):
    print("Inside Fix Fingers")
    for i in range(0,m):
      self.finger[i] = self.find_successor(self.id + 2**i)
      if i == 0:
        self.finger[0] = self.finger[i]

  def display(self):
    succ = self.finger[0].id if self.finger[0] else None
    pred = self.predecessor.id if self.predecessor else None
    finger_table = ",".join(str(x.id) for x in self.finger)
    print("< Node {}: suc {}, pre {}: finger {}".format(self.id, succ, pred, finger_table))

  def find_successor(self, val):
    if not (is_id_in_range(self.id, self.finger[0].id, val, False, True)):
      return self.finger[0]
    else:
      n0 = self.finger[0].closest_preceding_finger(val)
      if n0 == self:
        return self
      return n0.find_successor(val)

  def closest_preceding_finger(self, val):
    for i in range(m-1,-1,-1):
      curr_finger_id = self.finger[i].id
      if is_id_in_range(self.id, val, curr_finger_id, False, False):
        return self.finger[i]
    return self


def execute(method, value=None, value1=None):
  if method == "add" and value != None:
    if value in ring:
      print("Node {} exists".format(value))
    else:    
      node = Node(value)
      ring[value] = node
      print("Added node {}".format(value))
  elif method == "join" and value != None and value1 != None:
    n = ring[value]
    n1 = ring[value1]
    n.join(n1)
  elif method == "drop":
    print("Inside Drop")
  elif method == "fix":
    print("Inside Fix")
    self.fix_fingers()
  elif method == "stab" and value != None:
    print("Inside Stab")
    node = ring[value]
    node.stabilize()
  elif method == "show" and value:
    index = (value%ring_length) - 1
    node = ring[index]
    if node:
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
  print(operands)
  if len(operands) == 3:
    method = operands[0].lower()
    value1 = int(operands[1])
    value2 = int(operands[2])
    if value1 > (2**m - 1) or value2 > (2**m -1):
      return "invalid"
    execute(method, value1, value2)
  elif len(operands) == 2:
    method = operands[0].lower()
    value = int(operands[1])
    if value > (2**m -1):
      return "invalid"
    execute(method, value)
  elif len(operands) == 1:
    method = operands[0].lower()
    execute(method)
  else:
    return "invalid"


def execute_file_instructions(filename, m):
  with open(filename) as f:
    for line in f:
      print(line)
      parse_and_execute(line,m)

if __name__ == '__main__':
  m = 0
  ring_length = 0
  ring = {}
  args = sys.argv
  print(args)
  if len(args) == 4:
    test_file = args[2]
    m = int(args[3])
    ring_length = int(2**m)
    execute_file_instructions(test_file, m)
  elif len(args) == 2:
    m = int(args[1])
    ring_length = int(2**m)
    while(True):
      print("\n>")
      instruction = input()
      flag = parse_and_execute(instruction, m)
      if flag == "end":
        break
      elif flag == "invalid":
        print("Invalid input")
  else:
    print("\nInvalid number of arguments")

