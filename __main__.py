import sys
import os
import vm_parse

#######################################
# DATA
#######################################

# Track all arithmetic & logical stack operations.
A_L_COMMANDS = [
  "add",
  "sub",
  "neg",
  "and",
  "or",
  "not",
  "eq",
  "lt",
  "gt"
]

#######################################
# FUNCTIONS
#######################################

# Convert VM code line to Hack assembly.
# See vm_parse.py for parsing logic.
def to_assembly(line, index, vm_file_base_name):
  words = line.split()

  if words[0] == "push":
    if words[1] == "constant":
      return vm_parse.parse_push_const(words)
    if words[1] == "temp":
      return vm_parse.parse_push_temp(words)
    if words[1] == "pointer":
      return vm_parse.parse_push_pointer(words)
    if words[1] == "static":
      return vm_parse.parse_push_static(words, vm_file_base_name)
    if words[1] in ["local", "argument", "this", "that"]:
      return vm_parse.parse_push_segment(words)

  if words[0] == "pop":
    if words[1] == "temp":
      return vm_parse.parse_pop_temp(words)
    if words[1] == "pointer":
      return vm_parse.parse_pop_pointer(words)
    if words[1] == "static":
      return vm_parse.parse_pop_static(words, vm_file_base_name)
    if words[1] in ["local", "argument", "this", "that"]:
      return vm_parse.parse_pop_segment(words)

  if words[0] == "add":
    return vm_parse.parse_add()
  if words[0] == "sub":
    return vm_parse.parse_sub()
  if words[0] == "and":
    return vm_parse.parse_and()
  if words[0] == "or":
    return vm_parse.parse_or()
  if words[0] == "not":
    return vm_parse.parse_not()
  if words[0] == "neg":
    return vm_parse.parse_neg()
  if words[0] == "eq":
    return vm_parse.parse_eq(index)
  if words[0] == "gt":
    return vm_parse.parse_gt(index)
  if words[0] == "lt":
    return vm_parse.parse_lt(index)

  return vm_parse.not_found(line)

# Given a file path for a .vm file, e.g. /path/to/stuff_file.vm,
# or a directory path, e.g. path/to/stuff_dir,
# Return just the name of the file w/o an extension, e.g. stuff_file
# or the directory name, e.g. stuff_dir
def extract_from_path(file_path):
  try:
    if file_path[-1] == '/':
      file_path = file_path[:-1]

    slash_pos = file_path.rindex('/')

    return file_path[(slash_pos + 1):].replace('.vm', '')
  except ValueError:
    return file_path.replace('.vm', '')

# Given a VM instruction,
# strip out any content preceded by "//".
def strip_comments(line):
  comment_index = None

  try:
    comment_index = line.index("//")
  except ValueError:
    pass

  if comment_index is None:
    return line
  else:
    return line[:comment_index]


# Check if a given line from a .vm file is valid VM code.
def is_command(line):
  # Split command into words.
  words = line.split()

  # Identify commands.
  if len(words) == 1 and words[0] in A_L_COMMANDS:
    return True
  elif len(words) == 2:
    if words[0] in ["goto", "if-goto", "label"]:
      return True
  elif len(words) == 3:
    if words[0] in ["push", "pop"]:
      return True

  if line.strip() != "" and line[:2] != "//":
    print(f'WARNING! Unrecognized line: {line}')

  return False

# Create a list of Hack assembly instructions from VM code.
def parse_vm(vm_file_name):
  vm_file = open(vm_file_name)
  vm_file_base_name = extract_from_path(vm_file_name)

  output = []

  for index, line in enumerate(vm_file.readlines()):
    line = strip_comments(line)

    if is_command(line):
      output.extend(
        to_assembly(line.strip(), index, vm_file_base_name)
      )

  return output

# Given a list of ASM instructions and a VM file name,
# create an ASM file and write ASM instructions to it.
def write_asm(asm_instructions, vm_file_name):
  asm_file_name = vm_file_name.replace('.vm', '.asm')

  asm_file = open(asm_file_name, 'w')

  for instruction in asm_instructions:
    asm_file.write(f'{instruction}\n')

  asm_file.close()

# Given a directory,
# create an ASM file within the directory with the same name.
def create_asm_for_dir(vm_dir_name):
  # Extract the directory name.
  extracted_name = extract_from_path(vm_dir_name)

  # Create a new ASM file within the directory.
  asm_file_name = f'{vm_dir_name}/{extracted_name}.asm'
  asm_file = open(asm_file_name, 'w')

  asm_file.close()

  return asm_file_name

# Given a directory of VM files and an ASM file,
# parse each VM file and write result to ASM.
def write_asm_from_dir(vm_dir_name, asm_file_name):
  asm_file = open(asm_file_name, 'a')

  for file_name in os.listdir(vm_dir_name):
    if '.vm' not in file_name:
      continue

    asm_file.write(f'// --------------\n')
    asm_file.write(f'// {vm_dir_name}/{file_name} \n')
    asm_file.write(f'// --------------\n')

    asm_instructions = parse_vm(f'{vm_dir_name}/{file_name}')

    for instruction in asm_instructions:
      asm_file.write(f'{instruction}\n')

  asm_file.close()

#######################################
# MAIN
#######################################

# TO USE:
# python ./path/to/dir/vm_translator ./path/to/file.vm
# OR
# python ./path/to/dir/vm_translator ./path/to/dir_of_vms
def main():
  vm_input = sys.argv[1]

  if os.path.isdir(vm_input):
    # Create an ASM file within the directory.
    asm_file_name = create_asm_for_dir(vm_input)

    # Parse each VM file and write to ASM file.
    write_asm_from_dir(vm_input, asm_file_name)
  elif os.path.isfile(vm_input):
    # Parse the VM file.
    asm_instructions = parse_vm(vm_input)
    # Write the ASM file.
    write_asm(asm_instructions, vm_input)
  else:
    print('Input is not a file or directory. Please try again.')

if __name__ == "__main__":
  main()
