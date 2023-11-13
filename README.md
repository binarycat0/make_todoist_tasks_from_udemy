# make_todoist_tasks_from_udemy
Make todoist list of tasks from Udemy course


## cli
```shell
~/> python make_tasks.py --help
Usage: make_tasks.py [OPTIONS] COMMAND [ARGS]...

  Download the course data and then parse it and save into todoist format.

  1. run link command and get the "link"

  2. download data by the "link"

  3. run todoist command

  4. upload files to todoist
        
Options:
  -c, --course_id TEXT  [required]
  --help                Show this message and exit.

Commands:
  link
  todoist
```

### link 
```shell
~/> python make_tasks.py -c 123 link --help
Usage: make_tasks.py link [OPTIONS]

  Get the link for downloading the course data

Options:
  --help  Show this message and exit.

~/> python make_tasks.py -c 123 link    
https://www.udemy.com/api-2.0/courses/123/subscriber-curriculum-items?caching_intent=True&fields%5Basset%5D=title%2Ctime_estimation&fields%5Bchapter%5D=title&fields%5Blecture%5D=title%2Casset&fields%5Bpractice%5D=title&fields%5Bquiz%5D=title&page=1&page_size=1000
```

### todoist
```shell
~/> python make_tasks.py -c 123 todoist --help
Usage: make_tasks.py todoist [OPTIONS]

  Parse the downloaded course data and save files in todoist CSV format.

Options:
  -f, --from_file FILENAME  [required]
  -o, --output_dir PATH     [required]
  -b, --bunch_size INTEGER  [default: 10]
  --help                    Show this message and exit.
  
~/> python make_tasks.py -c 123 todoist -f /tmp/course_data.json -o /tmp
Result has written to file: /tmp/result_123_0.csv
```

## Download the Course data to `*.json` file
    
    # get link to the Course data
    ~/>python make_tasks.py -c <COURSE_ID> link
    https://www.udemy.com/api-2.0/courses/123/subscriber-curriculum-items?caching_intent=True&fields%5Basset%5D=title%2Ctime_estimation&fields%5Bchapter%5D=title&fields%5Blecture%5D=title%2Casset&fields%5Bpractice%5D=title&fields%5Bquiz%5D=title&page=1&page_size=1000

1. Run the command above with YOUR_COURSE_ID
2. Copy & paste it into your browser you logged in to udemy.com
3. Copy & save the content to `/home/some/path/course_data.json`
> If your course is big you will find the "next" link in your response. It means you should click on and download the next response to `/home/some/path/course_data_1.json` file and repeat again until "next" field is empty.  

5. in the end you sould have the bunch of files or just one
```text
/home/some/path/course_data.json
/home/some/path/course_data_1.json
```

The responses should contain the following json structure

```text
Response:
    count: int
    next: link
    previous: link
    result: List[Union[Chapter, Lecture, Quiz]]
    
Chapter:
    _class: str
    id: int
    title: str
    
Quiz(Chapter): ...
Asset(Chapter): ...

Lecture(Chapter): 
    ...
    asset: Optional[Asset]   
```

```json
{
    "count": 1,
    "next": "https://",
    "previous": null,
    "results":
    [
        {
            "_class": "chapter",
            "id": 123,
            "title": "Getting Started"
        },
        {
            "_class": "lecture",
            "id": 123,
            "title": "Course Introduction",
            "asset":
            {
                "_class": "asset",
                "id": 123,
                "title": "Promo_music.mp4",
                "time_estimation": 125
            }
        }
    ]
}
```

## Parse files to todoist format

About todoist format 
- https://todoist.com/help/articles/format-a-csv-file-to-import-into-todoist-UVUXTmm6

```shell
~/> python make_tasks.py -c 123 todoist -f /home/some/path/course_data.json -f /home/some/path/course_data_1.json -o /tmp

Result has written to file: /tmp/result_123_0.csv
Result has written to file: /tmp/result_123_15.csv
```



Upload the files you got to Todoist application.
```text
/tmp/result_123_0.csv
```