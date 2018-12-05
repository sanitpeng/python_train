cd ~/abu/data/tdx_csv
pwd
rm -rf Volumes
rm -f export.tar.bz2
tar cvjf export.tar.bz2 /Volumes/export
tar xvjf export.tar.bz2
cd Volumes/export
for file in ./*
do
    
    ext="${file##*.}"
    if test -f $file -a $ext == "csv"
    then
            echo 处理文件$file 
            sed -i "" '$d' $file
            sed -i '' "1 i\\
                date,open,high,low,close,volume,count
            " $file
    fi
done
cd -


