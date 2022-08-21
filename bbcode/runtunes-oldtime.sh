set -x
function usage {
  echo usage: $0 abcfile [ create-date ]
}

[ -z "$1" ] &&  { usage; exit 1; }
[[ $1 == '*.abc' ]] && { usage; exit; }

bn=$(basename $1 .abc )

[ -z "$2" ] || {
  touch -t $2 $1
}

abcm2ps $1 -X -x

./addindex2.py -f oldtime-frontmaterial.html -C --all -s oldtime.css Out.xhtml
[ -s Out.idx.xhtml ] && mv Out.idx.xhtml $bn.htm
