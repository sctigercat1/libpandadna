interrogate -D__inline -DCPPPARSER -DP3_INTERROGATE=1 -D__cplusplus -fnames -string -refcount -assert -SC:\Panda3D-1.8.1\include\parser-inc -SC:\Panda3D-1.8.1\include -IC:\Panda3D-1.8.1\include -oc libpandadna_igate.cxx -od libpandadna.in -python-native *.h -module libpandadna -library libpandadna -Dvolatile=
interrogate_module -python-native -module libpandadna -library libpandadna -oc libpandadna_module.cxx libpandadna.in