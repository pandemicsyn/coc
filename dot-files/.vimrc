call pathogen#infect()
call pathogen#helptags()
syntax on
set ai ts=4 tw=0 sw=4 expandtab
set hlsearch
" set paste
set title
filetype plugin on
filetype plugin indent on
" Increase indentation after open-braces and match close-brace indentation to
" their open-brace indentations.
set smartindent
set backspace=indent,eol,start
" Automatically jump to where the search matches as it is being typed.
set incsearch
" Try to keep 4 extra lines of context at the top and bottom of the screen.
set scrolloff=4
" Turns on syntax highlighting.
syn enable
" Turn on mouse mode.
set mouse=a
set ttymouse=xterm2
" highlight lines over 79 cols, spaces at the end of lines and tab characters
highlight BadStyle ctermbg=darkgray ctermfg=yellow
match BadStyle "\(\%>79v.\+\|\t\| \+$\)"
" pep8
let g:pep8_map='<leader>8'

""""""""""""""""""""""""""""""
" => Statusline
""""""""""""""""""""""""""""""
" Always hide the statusline
set laststatus=2

" Format the statusline
set statusline=\ %{HasPaste()}%F%m%r%h\ %w\ \ CWD:\ %r%{CurDir()}%h\ \ \ Line:\ %l/%L:%c


function! CurDir()
    let curdir = substitute(getcwd(), '/Users/fhines/', "~/", "g")
    return curdir
endfunction

function! HasPaste()
    if &paste
        return 'PASTE MODE  '
    else
        return ''
    endif
endfunction
