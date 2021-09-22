# bazel-goto-build
Tool to enable jumping to the target containing the source file (relies on [buildozer](https://github.com/bazelbuild/buildtools))

### Example vim integration (assuming goto_build exists on your path and points to `goto_build.py`):
```
function! s:gotobuild() abort
    let l:file_path=expand('%:p')
    let l:command="goto_build -i " . l:file_path
    echo l:command
    let l:result=trim(system(l:command))
    if l:result == ""
      echo 'No corresponding BUILD file found'
    else
      let l:result_list=split(l:result, ':')
      let l:build_file_name=l:result_list[0]
      let l:build_file_line=l:result_list[1]
      execute 'edit +' . l:build_file_line l:build_file_name
      execute 'normal! zz'
    endif
endfunction
command! -complete=command GOTOBuild call <SID>gotobuild()
nnoremap <silent> mB :GOTOBuild<CR>
```
