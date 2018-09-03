### ZipFileHelper
---

- 目录
{:toc}

ZipFileHelper 提供了对于单文件、多文件的无密码、有密码压缩，解压，向zip压缩包里添加文件，从压缩包直接删除文件等方法。

该模块目前仅兼容python3。

ZipFileHelper 基于zlib和pyminizip，使用之前请先安装以下模块：

install zlib

    ubuntu:
    $ sudo apt-get install zlib1g-dev
    mac:
    $ sudo port install zlib
    windows：
    可在"http://gnuwin32.sourceforge.net/packages/zlib.htm"下载安装包安装

install pyminizip

    $ pip install pyminizip

    
ZipFileHelper提供了四个静态方法，四个类成员方法供使用者使用：

---
### zip_file

将单个或多个源文件和目录压缩为一个zip文件。该方法为静态方法。
##### Syntax
```
zip_file(src_filepath, dst_zip_filename=None, entryname=None, **karg)
```
##### 参数

- src_filepath 
待压缩的单个或多个文件和目录，文件路径可为相对路径或绝对路径。参数类型为str或list。

- dst_zip_filename 
生成的zip文件的路径（包含文件名），可为相对路径或绝对路径。若不填或为空，此时将取相对路径，生成的zip与源文件在同一目录下，zip文件名与源文件名相同。
- entryname 
添加到压缩包里的条目名列表。若不填或为空，此时若源文件与dst_zip_filename具有相同目录结构（D:\\test\\abc\\def\\g.txt,D:\\test\\a.zip视为具有相同目录结构），则源文件在压缩包内仍保持其目录结构（\\abc\\def\\g.txt），否则，则只取文件名（\\g.txt）。若不为空，则entryname与src_filepath呈一一对应关系。
**karg| 
---|
若使用者需要加密压缩，请使用password关键字参数。

##### 返回值
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
##### 参数

- src_zip_filename 
待解压的单个压缩包文件。

- dst_dir_path 
解压后文件所处目录。若不填或为空，此时压缩包文件将会解压到压缩包文件父目录下。若不为空且不存在目标目录，则会自动创建目标目录。
- password 
解压所需密码。默认为空，此时压缩包应未加密。

##### 返回值
解压缩成功返回True，失败返回False。

##### 示例

```
ZipFileHelper.unzip_file('good.zip', test)
ZipFileHelper.unzip_file('good.zip', None, '123')
```
---
### zip_add

向zip压缩包内添加单个或多个文件，只允许将文件以未加密的形式添加到压缩包。该方法为静态方法。
##### Syntax
```
zip_add(src_zip_filename, filename_list, entryname_list=None)
```
##### 参数

- src_zip_filename 
待添加文件的zip压缩包。

- filename_list 
待添加到压缩包内的文件列表，文件路径可为相对路径或绝对路径。参数类型可为str和list。
- entryname_list 
添加到压缩包内的条目名列表。默认为空，此时若源文件与src_zip_filename具有相同目录结构（D:\test\abc\def\g.txt,D:\test\a.zip视为具有相同目录结构），则源文件在压缩包内仍保持其目录结构（\abc\def\g.txt），否则，则只取文件名（\g.txt）。若不为空，则entryname_list与filename_list呈一一对应关系。

##### 返回值
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
##### 参数

- src_zip_filename 
待删除文件的zip压缩包。

- entryname_list 
待删除的文件列表。参数类型可为str和list。

##### 返回值
成功删除文件返回True，失败返回False。

##### 示例

```
ZipFileHelper.zip_del('good.zip', 'test\\abc\\1.txt')
ZipFileHelper.zip_del('good.zip', ['1.txt', 'a.txt'])
```
##### 备注
若zip压缩包含有密码则会导致删除失败，请确保源zip不含有密码。

---
### create

新建一个空zip压缩包文件。该方法为类成员方法。
##### Syntax
```
create(zip_filename)
```
##### 参数

- zip_filename 
新建压缩包文件名。

##### 返回值
该方法没有返回值。

##### 示例
参见close方法示例。
##### 备注
操作完毕后，需使用close()方法关闭。

---
### push

向zip压缩包文件添加单个或多个文件和目录，使用该函数前请首先使用create函数创建一个压缩文件。该方法为类成员方法。
##### Syntax
```
push(filename_list, entryname_list=None)
```
##### 参数

- filename_list 
待添加到压缩包内的单个或多个文件和目录，文件路径可为相对路径或绝对路径。参数类型可为str和list。
- entryname_list 
添加到压缩包内的条目名列表。默认为空，此时若源文件与src_zip_filename具有相同目录结构（D:\test\abc\def\g.txt,D:\test\a.zip视为具有相同目录结构），则源文件在压缩包内仍保持其目录结构（\abc\def\g.txt），否则，则只取文件名（\g.txt）。若不为空，则entryname_list与filename_list呈一一对应关系。
##### 返回值
该方法没有返回值。

##### 示例
参见close方法示例。
##### 备注
操作完毕后，需使用close()方法关闭。

---
### pull

根据filename_list从zip压缩包文件中提取指定文件，使用该函数前请首先使用create函数创建一个压缩文件。该方法为类成员方法。
##### Syntax
```
pull(entryname_list, filename_list=None)
```
##### 参数

- entryname_list 
待提取的文件列表。参数类型可为str和list。
- filename_list 
提取出的文件名列表。默认为空，此时提取出的文件名与zip压缩包内文件名相同。若filename_list是空或相对路径，则提取出的文件与zip压缩包文件在同一目录下。若不为空，则filename_list与entryname_list呈一一对应关系。
##### 返回值
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
##### 参数
该方法没有参数。
##### 返回值
该方法没有返回值。

##### 示例
```
zip_object = ZipFileHelper()
zip_object.create('test.zip')  # 创建一个zip
zip_object.push(['1.txt', '2.txt'])  # 将1.txt 和 2.txt 添加到压缩包
zip_object.push('3.txt')  # 将3.txt 添加到压缩包
zip_object.pull('3.txt', 'a.txt')  # 从压缩包内提取3.txt 并命名为a.txt
zip_object.close()  # 操作完毕，关闭
```
