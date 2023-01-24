import mimetypes
from pathlib import Path
import pylexibank
from csvw.dsv import UnicodeWriter
from clldutils.jsonlib import load

from pytsammalex import lexibank
from pytsammalex.gbif import GBIF
import pylexibank
import attr

from pycldf import Dataset

@attr.s
class Language(pylexibank.Language):
    Description = attr.ib(default=None)


class Dataset(lexibank.Dataset):
    dir = Path(__file__).parent
    id = "heathdogon"

    language_class = Language

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw_dir`, e.g.
        to download a temporary TSV file and convert to persistent CSV:

        >>> with self.raw_dir.temp_download("http://www.example.com/e.tsv", "example.tsv") as data:
        ...     self.raw_dir.write_csv('template.csv', self.raw_dir.read_csv(data, delimiter='\t'))
        """

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        A `pylexibank.cldf.LexibankWriter` instance is available as `args.writer`. Use the methods
        of this object to add data.
        """
        self.add_image_schema(args.writer)

        images = load(self.raw_dir / 'cdstar.json')

        for c in self.concepts:
            args.writer.add_concept(**c)

        for l in self.raw_dir.read_csv('languages.csv', dicts=True):
            args.writer.add_language(**{k: v for k, v in l.items() if k[0].isupper()})

        for name in self.raw_dir.read_csv('names.csv', dicts=True):
            args.writer.add_form(
                Language_ID=name['languages__id'],
                Parameter_ID=name['taxa__id'],
                Value=name['name'],
                Form=name['name'],
            )

        for row in self.raw_dir.read_csv('images.csv', dicts=True):
            img = images[row['id']]
            args.writer.objects['MediaTable'].append(dict(
                # id, taxa__id, tags, mime_type, src, creator, date, place, gps, permission, source, comments, Name,
                # canonicalName, GBIF_ID, GBIF_NAME, rank, kingdom, phylum, class_, order, family, genus, kingdomKey,
                # phylumKey, classKey, orderKey, familyKey, genusKey
                ID=row['id'],
                Name=row['src'],
                Taxon_ID=row['taxa__id'],
                Media_Type=row['mime_type'] or mimetypes.guess_type(img['web'])[0],
                objid=img['objid'],
                bitstreamid=img['web'],
            ))