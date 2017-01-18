#!/usr/bin/env python3

import base64
import mimetypes
import os
from xml.dom import minidom

import pendulum
import html2text
from lxml import etree


def sanitize_filename(fname):
    # this should be way more sophisticated. probably use a slug generator (see django)
    return fname.replace('/', '')


def el(parent, tag, text, **attrs):
    element = etree.SubElement(parent, tag, **attrs)
    element.text = text
    return element


def create_note_plist(**params):
    root = etree.Element('plist')
    root.set('version', '1.0')
    data_dict = etree.Element('dict')
    el(data_dict, 'key', 'CreationDate')
    el(data_dict, 'date', text=params.get('created'))
    root.append(data_dict)
    doc = minidom.parseString(etree.tostring(root, encoding='utf-8'))
    return doc.toprettyxml(indent="  ")


def main(args):
    tree = etree.parse(args.file)

    for child in tree.getroot():
        params = {
            'title': child.find('title').text,
            'created': pendulum.parse(child.find('created').text).to_atom_string()
        }

        fname = sanitize_filename(params['title'])

        if args.out:
            fname = os.path.join(args.out, fname)

        ext = 'txt' if args.to_text else 'html'

        with open('%s.plist' % fname, 'w') as f:
            f.write(create_note_plist(**params))

            content = child.find('content').text
            doc = etree.fromstring(content.encode('utf-8'))
            # check type
            media_node = doc.find('en-media')
            if media_node is not None:
                mime_type = media_node.attrib.get('type')
                data = child.find('resource/data').text
                if mime_type == 'application/pdf':
                    with open('%s.%s' % (fname, 'pdf'), 'wb') as f:
                        f.write(base64.b64decode(data))
                elif mime_type.startswith('image/'):
                    image_dir = os.path.join(args.out, 'NBImages')
                    image_ext = mimetypes.guess_extension(mime_type)

                    # python returns .jpe for jpeg. this is pretty uncommon
                    if image_ext == '.jpe':
                        image_ext = '.jpg'

                    # create image name using timestamp
                    image_uniquename = pendulum.now().format('%Y%m%d-%H%M%S')
                    image_fname = "%s%s" % (image_uniquename, image_ext)

                    # create image dir for notebook
                    if not os.path.exists(image_dir):
                        os.makedirs(image_dir)

                    # check if image exists
                    if os.path.exists(os.path.join(image_dir, image_fname)):
                        index = 0
                        while os.path.exists(os.path.join(image_dir, "%s-%s%s" % (image_uniquename, index, image_ext))):
                            index += 1
                        image_fname = "%s-%s%s" % (image_uniquename, index, image_ext)

                    image_path = os.path.join(image_dir, image_fname)

                    with open(image_path, 'wb') as f:
                        f.write(base64.b64decode(data))

                    content = '<div><img src="NBImages/%s"></div>' % image_fname
                    with open('%s.%s' % (fname, ext), 'w') as f:
                        f.write(content)
                else:
                    print('Unable to convert note %s: en-media of type %s is not yet supported.' % (
                        params['title'], mime_type))
                    # print(data)
            else:
                if args.to_text:
                    content = html2text.html2text(content)
                with open('%s.%s' % (fname, ext), 'w') as f:
                    f.write(content)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument("--to_text", help="Convert HTML Notes to Text Notes", action="store_true")
    parser.add_argument("--out", help="Output Directory")
    args = parser.parse_args()
    main(args)
