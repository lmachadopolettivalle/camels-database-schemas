from setuptools import setup

setup(
    name='camels_database',
    version='0.1.0',    
    description='Package for querying CAMELS Sql Database',
    url='https://github.com/lmachadopolettivalle/camels-database-schemas',
    author='Luis Fernando Machado Poletti Valle',
    author_email='luisfernando.machadopoletti@gmail.com',
    license='BSD 2-clause',
    packages=['camels_database'],
    install_requires=['matplotlib',
                      'numpy',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

