import argparse, pprint, codecs
pp = pprint.PrettyPrinter( indent=4 )

info = {
    'header': {}
    , 'sections': []
}

def parseHeader( file ):
    # 13 bytes
    info['header']['signature'] = file.read( 8 )
    info['header']['start_of_fields'] = file.read( 1 )
    info['header']['segment'] = file.read( 2 )
    info['header']['end_of_fields'] = file.read( 2 )

def parseSectionDescriptor( file ):
    # 76 bytes
    descriptor = {}

    sec_type = file.read( 16 ).split( b'\x00' )[0].decode( 'ascii' )
    descriptor['type'] = sec_type

    next_offset = int.from_bytes( file.read( 8 ), 'little' )
    descriptor['next_offset'] = next_offset

    size = int.from_bytes( file.read( 8 ), 'little' )
    descriptor['size'] = size

    file.read( 40 ) # padding
    descriptor['checksum'] = codecs.encode( file.read( 4 ),  'hex' ).decode( 'ascii' ).upper()

    info['sections'].append( descriptor )

    pp.pprint( descriptor )

    if 'volume' == sec_type:
        # 94 bytes
        file.read( 4 ) # reserved

        chunks = int.from_bytes( file.read( 4 ), 'little' )
        print( '\tChunks: {}'.format( chunks ) )

        sectors_per_chunk = int.from_bytes( file.read( 4 ), 'little' )
        print( '\tSectors per Chunk: {}'.format( sectors_per_chunk ) )

        bytes_per_sector = int.from_bytes( file.read( 4 ), 'little' )
        print( '\tBytes per Sector: {}'.format( bytes_per_sector ) )

        sectors = int.from_bytes( file.read( 4 ), 'little' )
        print( '\tSectors: {}'.format( sectors ) )

        file.read( 20 ) # reserved
        file.read( 45 ) # padding
        file.read( 5 ) # signature
        file.read( 4 ) # checksum
    elif 'digest' == sec_type:
        # 80 bytes
        md5 = file.read( 16 ).hex().upper()
        print( '\tMD5: {}'.format( md5 ) )

        sha1 = file.read( 20 ).hex().upper()
        print( '\tSHA1: {}'.format( sha1 ) )

        file.read( 40 ) # padding
        file.read( 4 ) # checksum
    elif 'hash' == sec_type:
        # 36 bytes
        md5 = file.read( 16 ).hex().upper()
        print( '\tMD5: {}'.format( md5 ) )

        file.read( 16 ) # unknown
        file.read( 4 ) # checksum

    file.seek( next_offset, 0 )

    #currentOffset = file.tell()
    #print( 'current offset', currentOffset )
    #print( 'seeking to', offset )
    #file.seek( offset, 0 )
    #print( 'reading', size )
    #data = file.read( size )
    #print( str( data ) )
    #print( 'rewind to', currentOffset )
    #file.seek( currentOffset, 0 )

    return sec_type

def parse( file ):
    parseHeader( file )

    section_type = ''

    while not 'done' == section_type:
        section_type = parseSectionDescriptor( file )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='EnCase Info Tool'
        , description='Gives basic information about EnCase E01 and L01 files.'
        , epilog='2023 - Robert Sirois'
    )
    parser.add_argument( 'filename' )

    args = parser.parse_args()
    
    with open( args.filename, mode='rb' ) as bin_ewf:
        parse( bin_ewf )
