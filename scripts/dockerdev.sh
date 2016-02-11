alias jcurl='curl -s -H "Content-Type: application/json"'
alias jpp='python -m json.tool'

function jparse {
   python -c 'import sys, json; print json.load(sys.stdin)'$1
}
