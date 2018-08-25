### ZipFileHelper
---

ZipFileHelper 提供了对于单文件、多文件的无密码、有密码压缩，解压，向zip压缩包里添加文件，从压缩包直接删除文件等方法。

该模块目前仅兼容python3。

ZipFileHelper 基于zlib 和pyminzip，使用之前请先安装以下模块：

install zlib

    ubuntu:
    $ sudo apt-get install zlib1g-dev
    mac:
    $ sudo port install zlib
    windows请直接在官网下载安装包

install pyminizip

    $ pip install pyminizip

    
ZipFileHelper提供了四个静态方法，四个类成员方法供使用者使用：

---
### zip_file

将源文件或目录压缩为一个zip文件。该方法为静态方法。
##### Syntax
```
zip_file(src_filepath, dst_zip_filename=None, entryname=None, **karg)
```
##### Parameters

src_filepath| 
---|
待压缩的文件或目录，参数类型可为str和list。

dst_zip_filename| 
---|

生成的zip文件的路径（包含文件名）。默认为空，此时生成的zip与源文件在同一目录下。
entryname| 
---|
添加到压缩包里的条目名列表。默认为空，此时压缩包里文件名与源文件名相同。
**karg| 
---|
若使用者需要加密压缩，请使用password关键字参数。

##### Return Value
压缩成功返回True，失败返回False。

##### 示例

```
ZipFileHelper.zip_file('test')
ZipFileHelper.zip_file('1.txt', None, 'a.txt')
ZipFileHelper.zip_file(['1.txt', '2.txt'], 'good.zip', ['a.txt', 'b.txt'])
ZipFileHelper.zip_file(['2.jpg', '1.txt'], 'good.zip', None, password='123')
```
---
### unzip_file

将压缩包文件解压到指定目录。该方法为静态方法。
##### Syntax
```
unzip_file(src_zip_filename, dst_dir_path=None, password=None)
```
##### Parameters

src_zip_filename| 
---|
待解压的单个压缩包文件。

dst_dir_path| 
---|

解压后文件所处目录。默认为空，此时压缩包文件将会解压到压缩包文件父目录下。
password| 
---|
解压所需密码。默认为空，此时压缩包应未加密。

##### Return Value
解压缩成功返回True，失败返回False。

##### 示例

```
ZipFileHelper.unzip_file('good.zip', test)
ZipFileHelper.unzip_file('good.zip', None, '123')
```
---
### zip_add

向zip压缩包内添加文件。该方法为静态方法。
##### Syntax
```
zip_add(src_zip_filename, filename_list, entryname_list=None)
```
##### Parameters

src_zip_filename| 
---|
待添加文件的zip压缩包。

filename_list| 
---|

待添加到压缩包内的文件列表。参数类型可为str和list。
entryname_list| 
---|
添加到压缩包内的条目名列表。默认为空，此时添加到压缩包内的文件名与源文件名相同。

##### Return Value
添加成功返回True，失败返回False。

##### 示例

```
ZipFileHelper.zip_add('good.zip', '1.txt')
ZipFileHelper.zip_add('good.zip', '1.txt', 'a.txt')
```
##### 备注
请勿向压缩包内添加已存在的同名文件。

---
### zip_del

从zip压缩包中删除指定文件。该方法为静态方法。
##### Syntax
```
zip_del(src_zip_filename, entryname_list)
```
##### Parameters

src_zip_filename| 
---|
待删除文件的zip压缩包。

entryname_list| 
---|

待删除的文件列表。参数类型可为str和list。

##### Return Value
成功删除文件返回True，失败返回False。

##### 示例

```
ZipFileHelper.zip_del('good.zip', '1.txt')
ZipFileHelper.zip_del('good.zip', ['1.txt', 'a.txt'])
```
##### 备注
若zip压缩包含有密码则会导致删除失败，请确保源zip不含有密码。

---
### create

新建一个zip压缩包文件。该方法为类成员方法。
##### Syntax
```
create(zip_filename)
```
##### Parameters

zip_filename| 
---|
新建压缩包文件名。

##### Return Value
该方法没有返回值。

##### 示例
参见close方法示例。
##### 备注
操作完毕后，需使用close()方法关闭。

---
### push

向zip压缩包文件添加文件，使用该函数前请首先使用creat函数创建一个压缩文件。该方法为类成员方法。
##### Syntax
```
push(filename_list, entryname_list=None)
```
##### Parameters

filename_list| 
---|

待添加到压缩包内的文件列表。参数类型可为str和list。
entryname_list| 
---|
添加到压缩包内的条目名列表。默认为空，此时添加到压缩包内的文件名与源文件名相同。
##### Return Value
该方法没有返回值。

##### 示例
参见close方法示例。
##### 备注
操作完毕后，需使用close()方法关闭。

---
### pull

从zip压缩包文件中提取文件，使用该函数前请首先使用creat函数创建一个压缩文件。该方法为类成员方法。
##### Syntax
```
pull(entryname_list, filename_list=None)
```
##### Parameters

entryname_list| 
---|

待提取的文件列表。参数类型可为str和list。
filename_list| 
---|
提取后文件名列表。默认为空，此时提取出的文件名与zip压缩包内文件名相同。若filename_list是None或相对路径，则提取出的文件与zip压缩包文件在同一目录下。
##### Return Value
该方法没有返回值。

##### 示例
参见close方法示例。
##### 备注
操作完毕后，需使用close()方法关闭。

----
### close

zip压缩包文件操作完毕后进行关闭。该方法为类成员方法。
##### Syntax
```
close()
```
##### Parameters

该方法没有参数。
##### Return Value
该方法没有返回值。

##### 示例
```
zip = ZipFileHelper()
zip.create('test.zip')  # 创建一个zip
zip.push(['1.txt', '2.txt'])  # 将1.txt 和 2.txt 添加到压缩包
zip.push('3.txt')  # 将3.txt 添加到压缩包
zip.pull('3.txt', 'a.txt')  # 从压缩包内提取3.txt 并命名为a.txt
zip.close()  # 操作完毕，关闭
```
