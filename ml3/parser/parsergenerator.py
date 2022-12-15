if __name__ == "__main__":
    from packratparsergenerator import PackratParserGenerator
    pgen = PackratParserGenerator()
    pgen.set_dest_filepath(
        "ml3\\parser\\parser.py",
        override=True, relative_path=True)
    pgen.set_src_filepath(
        "ml3\\parser\\Grammar.txt",
        relative_path=True,
        override=True)
    pgen.generate(verbose=False)



    
