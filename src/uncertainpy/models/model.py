import numpy as np

class Model(object):
    """
    Class for storing the model to perform uncertainty quantification on.

    The ``run(**parameters)`` method must either be implemented or set to a
    function, and is responsible for running the model.
    If you want to calculate features directly from the original model results,
    but still need to postprocess the model results to perform the
    uncertainty quantification, you can implement the postprocessing in the
    ``postprocess(time, values)`` method.

    Parameters
    ----------
    adaptive : bool, optional
        True if the model is adaptive, meaning it has a varying number of
        return values. False if not. Default is False.
    labels : list, optional
        A list of label names for the axes when plotting the model.
        On the form ``["x-axis", "y-axis", "z-axis"]``, with the number of axes
        that is correct for the model output.
        Default is an empty list.
    run_function : {None, callable}, optional
        A function that implements the model. See the ``run`` method for
        requirements of the function. Default is None.

    Attributes
    ----------
    labels : list
        A list of label names for the axes when plotting the model.
        On the form ``["x-axis", "y-axis", "z-axis"]``, with the number of axes
        that is correct for the model output.
    adaptive : bool
        True if the model is adaptive, meaning it has a varying number of
        time values. False if not. Default is False.
    name : str
        Name of the model. Either the name of the class or the name of the
        function set as run.

    See Also
    --------
    uncertainpy.models.Model.run : The run method.
    uncertainpy.models.Model.postprocess : The postprocessing method.
    """
    def __init__(self,
                 run_function=None,
                 adaptive=False,
                 labels=[],
                 ignore=False):
                 # TODO fix and document ignore option

        self.adaptive = adaptive
        self.labels = labels
        self.ignore = ignore

        if run_function is not None:
            self.run = run_function
        else:
            self.name = self.__class__.__name__


    @property
    def run(self):
        """
        Run the model and return time and model result.

        This method must either be implemented or set to a function and is
        responsible for running the model. See Notes for requirements.

        Parameters
        ----------
        **parameters : A number of named arguments (name=value).
            The parameters of the model. These parameters must be assigned to
            the model, either setting them with Python, or
            assigning them to the simulator.

        Returns
        -------
        time : {None, numpy.nan, array_like}
            Time values of the model, if no time values returns None or
            numpy.nan.
        values : array_like
            Result of the model. Note that `values` myst either be regular
            (have the same number of points for different paramaters) or be able
            to be interpolated.
        info, optional
            Any number of info objects that is passed on to feature calculations.
            It is recommended to use a single dictionary with the information
            stored as key-value pairs.
            This is what the implemented features requires, as well as
            require that specific keys to be present.

        Raises
        ------
        NotImplementedError
            If no run method have been implemented or set to a function.

        Notes
        -----
        The ``run(**parameters)`` method must either be implemented or set to a
        function. Both options have the following requirements:

        1. ``run(**parameters)`` takes a number of named arguments which are
        the parameters to the model. These parameters must be assigned to
        the model, either setting them with Python, or
        assigning them to the simulator.

        2. ``run(**parameters)`` must return the time values (`time`) or equivalent
        and the model result (`values`). If the model have no time values,
        return None or numpy.nan instead. The first two values returned must be
        `time`, and `values`. Additionally, any number of info objects can be
        returned after `time`, and `values`. These info objects are optional and are
        passed on to ``model.postprocess``, ``features.preprocess``, and feature
        calculations.

        The model does not need to be implemented in Python, you can use any
        model/simulator as long as you are able to set the model parameters of
        the model from the run method Python and return the results from the
        model into the run method.

        The model results `time` and `values` are used to calculate the features, as
        well as the optional `info` objects returned.

        The model results must either be regular, be able to be interpolated, or
        be able to be postprocessed to a regular form, or a form that can
        be interpolated. This is because the uncertainty quantification methods
        needs results with the same number of points for each set of parameters
        to be able to perform the uncertainty quantification.

        If you want to calculate features directly from the original model results,
        but still need to postprocess the model results to perform the
        uncertainty quantification, you can implement the postprocessing in the
        ``postprocess(time, values, *info)`` method.

        See also
        --------
        uncertainpy.features : Features of models
        uncertainpy.features.Features.preprocess : Preprocessing of model results before feature calculation
        uncertainpy.model.Model.postprocess : Postprocessing of model result.
        """
        return self._run


    @run.setter
    def run(self, new_run_function):
        if not callable(new_run_function):
            raise TypeError("run() function must be callable")

        self._run = new_run_function
        self.name = new_run_function.__name__


    def set_parameters(self, **parameters):
        """
        Set all named arguments as attributes of the model class.

        Parameters
        ----------
        **parameters : A number of named arguments (name=value).
            All set as attributes of the class.
        """
        for parameter in parameters:
            setattr(self, parameter, parameters[parameter])



    def _run(self, **parameters):
        raise NotImplementedError("No run() method implemented or set in {class_name}".format(class_name=self.__class__.__name__))



    def postprocess(self, *model_result):
        """
        Postprocessing of the time and results from the model.

        No postprocessing is performed, and the direct model results are
        currently returned.
        If postprocessing is needed it should follow the below format.

        Parameters
        ----------
        *model_result
            Variable length argument list. Is the values that ``run()``
            returns. It contains `time` and `values`,
            and then any number of optional `info` values.
        time : {None, numpy.nan, array_like}
            Time values of the model. If no time values it should return None or
            numpy.nan.
        values : array_like
            Result of the model.
        info, optional
            Any number of info objects that is passed on to feature calculations.
            It is recommended to use a single dictionary with the information
            stored as key-value pairs.
            This is what the implemented features requires, as well as
            require that specific keys to be present.

        Returns
        -------
        time : {None, numpy.nan, array_like}
            Time values of the model, if no time values returns None or
            numpy.nan.
        values : array_like
            the postprocessed model results, `values` must either be regular
            (have the same number of points for different paramaters) or be able
            to be interpolated.

        Notes
        -----
        Perform a postprocessing of the model results before they are sent to
        the uncertainty quantification.
        The model results must either be regular or be able to be interpolated.
        This is because the uncertainty quantification methods
        needs results with the same number of points for each set of parameters
        to be able to perform the uncertainty quantification.

        ``postprocess(time, values)`` is implemented to make
        the model results regular, or on a form that can be interpolated.
        The results from the postprocessing is not
        used to calculate features, and is therefore used if you
        want to calculate features directly from the original model results,
        but still need to postprocess the model results to perform the
        uncertainty quantification.
        """
        return model_result[:2]


    def validate_run_result(self, model_result):
        """
        Validate the results from ``run()``.

        This method ensures the results from returns `time`, `values`, and optional
        info objects.

        Returns
        -------
        model_results
            Any type of model results returned by ``run()``.

        Raises
        ------
        ValueError
            If the model result does not fit the requirements.
        TypeError
            If the model result does not fit the requirements.

        Notes
        -----
        Tries to verify that at least, `time` and `values` are returned from ``run()``.
        ``run()`` should return on the following format
        ``return time, values, info_1, info_2, ...``.

        time : {None, numpy.nan, array_like}
            Time values of the model. If no time values it should return None or
            numpy.nan.
        values : array_like
            Result of the model.
        info, optional
            Any number of info objects that is passed on to feature calculations.
            It is recommended to use a single dictionary with the information
            stored as key-value pairs.
            This is what the implemented features requires, as well as
            require that specific keys to be present.
        """
        if isinstance(model_result, np.ndarray):
            raise ValueError("model.run() returns an numpy array. "
                             "This indicates only t or U is returned. "
                             "model.run() or model function must return "
                             "time and values "
                             "(return time, values | return None, values)")

        if isinstance(model_result, str):
            raise ValueError("model.run() returns an string. "
                             "This indicates only t or U is returned. "
                             "model.run() or model function must return "
                             "time and values "
                             " (return time, values | return None, values)")

        try:
            time, values = model_result[:2]
        except (ValueError, TypeError) as error:
            msg = "model.run() or model function must return time and values (return time, values | return None, values)"
            if not error.args:
                error.args = ("",)
            error.args = error.args + (msg,)
            raise