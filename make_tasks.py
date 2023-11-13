import contextlib
import csv
import dataclasses
import datetime
import json
import urllib.parse
from typing import List, Dict

import click


@dataclasses.dataclass
class Part:
    title: str
    duration: int

    def __repr__(self):
        return f'{self.title} {str(datetime.timedelta(seconds=self.duration))}'


@dataclasses.dataclass
class Chapter:
    title: str
    parts: List[Part] = dataclasses.field(default_factory=list)

    @property
    def duration(self):
        return sum((p.duration for p in self.parts))

    def __repr__(self):
        return f'{self.title} {str(datetime.timedelta(seconds=self.duration))}'


class Fields:
    TYPE = 'TYPE'
    CONTENT = 'CONTENT'
    DESCRIPTION = 'DESCRIPTION'
    PRIORITY = 'PRIORITY'
    INDENT = 'INDENT'
    AUTHOR = 'AUTHOR'
    RESPONSIBLE = 'RESPONSIBLE'
    DATE = 'DATE'
    DATE_LANG = 'DATE_LANG'
    TIMEZONE = 'TIMEZONE'
    DURATION = 'DURATION'
    DURATION_UNIT = 'DURATION UNIT'

    @classmethod
    def to_list(cls) -> List[str]:
        return [
            Fields.TYPE,
            Fields.CONTENT,
            Fields.DESCRIPTION,
            Fields.PRIORITY,
            Fields.INDENT,
            Fields.AUTHOR,
            Fields.RESPONSIBLE,
            Fields.DATE,
            Fields.DATE_LANG,
            Fields.TIMEZONE,
            Fields.DURATION,
            Fields.DURATION_UNIT,
        ]


class PRIORITY:
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4


class INDENT:
    I1 = 1
    I2 = 2
    I3 = 3
    I4 = 4


def parse_lecture(lecture_data: List[Dict]) -> List[Chapter]:
    result = []
    i = 0
    while i < len(lecture_data):
        if i >= len(lecture_data):
            break
        elif lecture_data[i]['_class'] != 'chapter':
            i += 1
            continue

        new_chapter = Chapter(lecture_data[i]['title'])
        result.append(new_chapter)

        j = i
        while True:
            j += 1
            if (
                    j >= len(lecture_data)
                    or lecture_data[j]['_class'] == 'chapter'
            ):
                break

            new_chapter.parts.append(
                Part(
                    lecture_data[j]['title'],
                    lecture_data[j].get('asset', {}).get('time_estimation', 0)
                )
            )
        i = j
    return result


@contextlib.contextmanager
def new_file(output_dir, course_id, index):
    output_file_name = f'{output_dir}/result_{course_id}_{index}.csv'
    with open(output_file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=Fields.to_list())
        writer.writeheader()
        yield writer
        print(f'Result has written to file: {output_file_name}')


def get_new_raw(**kw):
    new = {k: '' for k in Fields.to_list()}
    new.update(kw)
    return new


@click.group('cli')
@click.option('--course_id', '-c', required=True)
@click.pass_context
def cli(ctx, course_id):
    """Download the course data and then parse it and save into todoist format.\n
    1. run link command and get the "link"\n
    2. download data by the "link"\n
    3. run todoist command\n
    4. upload files to todoist
    """
    ctx.ensure_object(dict)
    ctx.obj['course_id'] = course_id


@cli.command()
@click.pass_context
def link(ctx):
    """Get the link for downloading the course data"""
    course_id = ctx.obj['course_id']
    udemy_host = 'https://www.udemy.com/api-2.0'

    args = urllib.parse.urlencode([
        ('caching_intent', 'True'),
        ('fields[asset]', 'title,time_estimation'),
        ('fields[chapter]', 'title'),
        ('fields[lecture]', 'title,asset'),
        ('fields[practice]', 'title'),
        ('fields[quiz]', 'title'),
        ('page', '1'),
        ('page_size', '1000')
    ])

    print(
        f'{udemy_host}/courses/{course_id}/subscriber-curriculum-items?{args}'
    )


@cli.command()
@click.option('--from_file', '-f', required=True, multiple=True, type=click.File())
@click.option('--output_dir', '-o', required=True, type=click.Path(exists=True, writable=True))
@click.option('--bunch_size', '-b', required=False, type=int, default=10, show_default=True)
@click.pass_context
def todoist(ctx, from_file: List, output_dir: str, bunch_size: int = 10):
    """Parse the downloaded course data and save files in todoist CSV format."""

    course_id = ctx.obj['course_id']
    lecture_parts = []
    for f in from_file:
        lecture_parts.extend(json.loads(f.read())['results'])

    chapters = parse_lecture(lecture_parts)
    i = 0
    while i < len(chapters):
        with new_file(output_dir, course_id, i) as writer:
            while True:
                writer.writerow(get_new_raw(
                    TYPE='task',
                    PRIORITY=PRIORITY.P3,
                    CONTENT=str(chapters[i]),
                    INDENT=INDENT.I1,
                    DURATION=chapters[i].duration,
                ))
                writer.writerow({})

                for part in chapters[i].parts:
                    writer.writerow(get_new_raw(
                        TYPE='task',
                        PRIORITY=PRIORITY.P4,
                        CONTENT=str(part),
                        INDENT=INDENT.I2,
                        DURATION=part.duration,
                    ))
                    writer.writerow({})

                i += 1
                if i >= len(chapters) or (i + 1) % bunch_size == 0:
                    break


if __name__ == '__main__':
    cli()
