DEBUG = 1

TYPES = {
  'number':0,
  'string':1,
  'boolean':2,
  'list':3,
  'dict':4,
  'null':5                
}

APPLY_TYPES = [
  TYPES['number'],
  TYPES['boolean'],
  TYPES['null']
]

obj_to_json_type = (k) ->
  return typeof k

type_for_enum = (k) ->
  for i in TYPES
    if TYPES[i] == k
      return i

class Node
  constructor: ->

  
        