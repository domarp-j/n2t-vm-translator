#######################################
# DATA
#######################################

SEG_TO_ADDR = {
  "local": "LCL",
  "argument": "ARG",
  "this": "THIS",
  "that": "THAT"
}

#######################################
# VM TO ASM PARSING FUNCTIONS
#######################################

def parse_push_const(words):
  return [
    f'// push constant {words[2]}',
    f'@{words[2]}',
    'D=A',
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1'
  ]

def parse_add():
  return [
    '// add',
    '@SP',
    'A=M',
    'A=A-1',
    'D=M',
    'A=A-1',
    'M=D+M',
    '@SP',
    'M=M-1'
  ]

def parse_sub():
  return [
    '// sub',
    '@SP',
    'A=M',
    'A=A-1',
    'D=M',
    'A=A-1',
    'M=M-D',
    '@SP',
    'M=M-1'
  ]

def parse_and():
  return [
    '// and',
    '@SP',
    'A=M',
    'A=A-1',
    'D=M',
    'A=A-1',
    'M=D&M',
    '@SP',
    'M=M-1'
  ]

def parse_or():
  return [
    '// or',
    '@SP',
    'A=M',
    'A=A-1',
    'D=M',
    'A=A-1',
    'M=D|M',
    '@SP',
    'M=M-1'
  ]

def parse_not():
  return [
    '// not',
    '@SP',
    'A=M',
    'A=A-1',
    'M=!M'
  ]

def parse_neg():
  return [
    '// neg',
    '@SP',
    'A=M',
    'A=A-1',
    'M=-M'
  ]

# index argument is used to create labels unique to the parsed instruction
def parse_eq(index):
  return [
    '// eq',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    'A=A-1',
    'D=M-D',
    f'@ISEQ{index}',
    'D;JEQ',
    '@SP',
    'A=M',
    'A=A-1',
    'M=0',
    f'@END{index}',
    '0;JMP',
    f'(ISEQ{index})',
    '@SP',
    'A=M',
    'A=A-1',
    'M=-1',
    f'(END{index})'
  ]

# index argument is used to create labels unique to the parsed instruction
def parse_gt(index):
  return [
    '// gt',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    'A=A-1',
    'D=M-D',
    f'@ISGT{index}',
    'D;JGT',
    '@SP',
    'A=M',
    'A=A-1',
    'M=0',
    f'@END{index}',
    '0;JMP',
    f'(ISGT{index})',
    '@SP',
    'A=M',
    'A=A-1',
    'M=-1',
    f'(END{index})'
  ]

# index argument is used to create labels unique to the parsed instruction
def parse_lt(index):
  return [
    '// lt',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    'A=A-1',
    'D=M-D',
    f'@ISLT{index}',
    'D;JLT',
    '@SP',
    'A=M',
    'A=A-1',
    'M=0',
    f'@END{index}',
    '0;JMP',
    f'(ISLT{index})',
    '@SP',
    'A=M',
    'A=A-1',
    'M=-1',
    f'(END{index})'
  ]

def parse_push_segment(words):
  segment = words[1]
  segment_label = SEG_TO_ADDR[segment]
  offset = words[2]

  return [
    f'// push {segment} {offset}',
    f'@{offset}',
    'D=A',
    f'@{segment_label}',
    'A=M+D',
    'D=M',
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1'
  ]

def parse_pop_segment(words):
  segment = words[1]
  segment_label = SEG_TO_ADDR[segment]
  offset = words[2]

  return [
    f'// pop {segment} {offset}',
    f'@{offset}',
    'D=A',
    f'@{segment_label}',
    'A=M+D',
    'D=A',
    '@R13',
    'M=D',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    '@R13',
    'A=M',
    'M=D'
  ]

def parse_push_temp(words):
  offset = words[2]

  return [
    f'// push temp {offset}',
    f'@{offset}',
    'D=A',
    f'@5',
    'A=A+D',
    'D=M',
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1'
  ]

def parse_pop_temp(words):
  offset = words[2]

  return [
    f'// pop temp {offset}',
    f'@{offset}',
    'D=A',
    f'@5',
    'A=A+D',
    'D=A',
    '@R13',
    'M=D',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    '@R13',
    'A=M',
    'M=D'
  ]

def parse_push_pointer(words):
  this_or_that = "THIS" if int(words[2]) == 0 else "THAT"

  return [
    f'// push pointer {words[2]}',
    f'@{this_or_that}',
    'D=M',
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1'
  ]

def parse_pop_pointer(words):
  this_or_that = "THIS" if int(words[2]) == 0 else "THAT"

  return [
    f'// pop pointer {words[2]}',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    f'@{this_or_that}',
    'M=D'
  ]

def parse_push_static(words, vm_file_base_name):
  offset = words[2]

  return [
    f'// push static {offset}',
    f'@{vm_file_base_name}.{offset}',
    'D=M',
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1'
  ]

def parse_pop_static(words, vm_file_base_name):
  offset = words[2]

  return [
    f'// pop static {offset}',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    f'@{vm_file_base_name}.{offset}',
    'M=D'
  ]

def parse_label(words):
  label_name = words[1]

  return [
    f'// label {label_name}',
    f'({label_name})'
  ]

def parse_goto(words):
  label_name = words[1]

  return [
    f'// goto {label_name}',
    f'@{label_name}',
    '0;JMP'
  ]

def parse_if_goto(words):
  label_name = words[1]

  return [
    f'// if-goto {label_name}',
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    f'@{label_name}',
    'D;JNE'
  ]

def parse_function(words):
  fname = words[1]
  local_count = words[2]

  instructions = []

  # Initialize comment and label.
  instructions = instructions + [
    f'// function {fname} {local_count}',
    f'({fname})'
  ]

  for _ in range(0, int(local_count)):
    instructions = instructions + parse_push_const(
      ['push', 'constant', 0]
    )

  return instructions

def parse_return():
  return [
    f'// return',
    # end_frame = LCL
    '@LCL',
    'D=M',
    '@R13',
    'M=D',
    # return_addr = *(end_frame - 5)
    'D=D-1',
    'D=D-1',
    'D=D-1',
    'D=D-1',
    'D=D-1',
    'A=D',
    'D=M',
    '@R14',
    'M=D',
    # *ARG = pop()
    '@SP',
    'M=M-1',
    'A=M',
    'D=M',
    '@ARG',
    'A=M',
    'M=D',
    # SP = ARG + 1
    '@ARG',
    'D=M+1',
    '@SP',
    'M=D',
    # THAT = *(end_frame - 1)
    '@R13',
    'A=M-1',
    'D=M',
    '@THAT',
    'M=D',
    # THIS = *(end_frame - 2)
    '@R13',
    'D=M-1',
    'A=D-1',
    'D=M',
    '@THIS',
    'M=D',
    # ARG = *(end_frame - 3)
    '@R13',
    'D=M-1',
    'D=D-1',
    'A=D-1',
    'D=M',
    '@ARG',
    'M=D',
    # LCL = *(end_frame - 4)
    '@R13',
    'D=M-1',
    'D=D-1',
    'D=D-1',
    'A=D-1',
    'D=M',
    '@LCL',
    'M=D',
    # goto return_addr
    '@R14',
    'A=M'
  ]

def not_found(line):
  return [
    '// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',
    f'// Parser does not recognize the command "{line}"',
    '// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',
  ]
