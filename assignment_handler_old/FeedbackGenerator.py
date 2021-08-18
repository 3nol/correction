import string
from pyparsing import *


def temp_gen(enumber: int) -> tuple[str, list[str]]:
    h_block = """{{%h_block%\n\nAssignment %%a_number%%\nPoints : %%points%%\n}}"""
    c_block = """{{%c_block%\n\n%%date%%\n%%c_name%%\n}}"""
    e_block = """{{%e_block%\n\n"""
    en = []
    for i in range(1, enumber + 1):
        e_block += f"""Exercise %%e_number{i}%%\n"""
        e_block += f"""Pass : %%p_ex{i}%%\n"""
        e_block += f"""##########################\n"""
        en.append(f"e_number{i}")
        en.append(f"p_ex{i}")
    e_block += "{{"
    return h_block + "\n" + e_block + "\n" + c_block, (["a_number", "points"] + en + ["date", "c_name"])


def get_par(t: str):
    RawWord = Word(re.sub('[{}" ]', '', string.printable))
    Token = Forward()
    Token << (RawWord |
              Group('"' + OneOrMore(RawWord) + '"') |
              Group('{{' + OneOrMore(Token) + '}}'))
    Phrase = ZeroOrMore(Token)

    return Phrase.parseString(t, parseAll=True)


def parse_entity(e: str):
    RawWord = Word(re.sub('[%" ]', '', string.printable))
    Token = Forward()
    Token << (RawWord |
              Group('"' + OneOrMore(RawWord) + '"') |
              Group('%%' + OneOrMore(Token) + '%%'))
    Phrase = ZeroOrMore(Token)
    return Phrase.parseString(e, parseAll=True)


def parse_entries(blocks: list, fields: dict):
    blocks_mod = []
    for block in blocks:
        mod_l = " ".join(block[1:-1]).split("\n")
        if mod_l[0][0] != "%":
            print("Missing Label")
        else:
            print(f"Parsing Block {mod_l[0].replace('%', '')}")
            bl = []
            for block in mod_l[1::]:
                print(parse_entity(block))
                t = []
                for ent in parse_entity(block):

                    if isinstance(ent, ParseResults):
                        print(f"replacing {ent[1]}")
                        try:
                            t.append(str(fields[ent[1]]))
                        except KeyError as e:
                            print(f"Missing '{ent[1]}' in Dict")
                            raise e
                    else:
                        t.append(ent)
                bl.append(" ".join(t))
            blocks_mod.append("\n".join(bl))
    print("".join(blocks_mod).strip())
    return blocks_mod


def generate_txt(fields: dict, file_path: str):
    with open(file_path, 'r') as template:
        lines = template.readlines()
    parsed_blocks = get_par("".join(lines))
    parse_entries(parsed_blocks, fields)