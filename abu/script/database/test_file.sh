for file in ./*
do
    
    ext="${file##*.}"
    if test -f $file -a $ext == "csv"
    then
            echo $file 是文件
            #sed -i "" '$d' $file
            #sed -i '' "1 i\\
            #    ,date,open,high,low,close,volume,count
            #" Volumes/export/SZ#300760.csv
    fi
done
