Preparation of the function
===========================

One key feature of the phs framework is the ergonomic handling. Care was taken to ensure that the entry barrier for use is as low as possible. 


As briefly described in :ref:`Quick Start` there are a few modifications needed to get your python script ready for use in the phs framework:

- Declare your phyton script as a function with a single argument named ``parameter``
- Delete (or comment out) all hard coded parameter definitions you want to control with phs tool
- add ``exec(parameter['hyperpar'],globals(),globals())``
- return a meaningful parameter

Let's assume you want to use the following pseudo code within phs to vary parameter ``x`` and ``size``::

   x = 5.6
   y = 500
   size = 103.56

   # some calculations

   print result

The function has to be::

   def my_function(parameter):
       exec(parameter['hyperpar'], globals(), globals())
       y = 500

       # some calculations

       return result

That's all.

