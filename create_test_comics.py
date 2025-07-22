import zipfile
import os

# Create a simple CBZ file for testing
test_dir = r'f:\src\Workspaces\Beets-ebooks\test_ebooks'
cbz_path = os.path.join(test_dir, 'Batman - Detective Comics 001.cbz')

# Create a simple ZIP file with some dummy image files
with zipfile.ZipFile(cbz_path, 'w') as cbz:
    # Add some dummy image files
    cbz.writestr('page001.jpg', b'fake image data')
    cbz.writestr('page002.jpg', b'fake image data')
    cbz.writestr('page003.jpg', b'fake image data')
    
    # Add ComicInfo.xml with metadata
    comic_info = '''<?xml version="1.0"?>
<ComicInfo>
    <Title>Detective Comics</Title>
    <Series>Batman</Series>
    <Number>1</Number>
    <Writer>Bob Kane</Writer>
    <Publisher>DC Comics</Publisher>
    <Year>1939</Year>
    <PageCount>3</PageCount>
    <Genre>Superhero</Genre>
    <Summary>The first appearance of Batman in Detective Comics.</Summary>
    <LanguageISO>en</LanguageISO>
</ComicInfo>'''
    cbz.writestr('ComicInfo.xml', comic_info.encode('utf-8'))

print(f"Created test CBZ file: {cbz_path}")
