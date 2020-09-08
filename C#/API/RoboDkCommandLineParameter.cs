// ----------------------------------------------------------------------------------------------------------
// Copyright 2020 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ----------------------------------------------------------------------------------------------------------

#region Namespaces

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;

#endregion

namespace RoboDk.API
{
    /// <summary>
    /// RoboDK command line parameter.
    /// See https://robodk.com/doc/en/RoboDK-API.html#CommandLine
    /// </summary>
    public class RoboDkCommandLineParameter
    {
        #region Fields

        internal static int DefaultApiServerPort = 20500;

        /// <summary>
        /// List of command line arguments.
        /// The order of options is important!!
        /// That is the main reason for using a List.
        /// A Dictionary is not ordered and adding an extra priority int attribute to use a SortedDictionary is error prone and
        /// overly complex.
        ///
        /// The Constructor will put the CommandLineOptions into a dictionary to access the options by there property name.
        /// </summary>
        private readonly List<CommandLineOption> _parameterList = new List<CommandLineOption>
        {
            new CommandLineOption<bool>(nameof(StartNewInstance), "NEWINSTANCE", false),
            new CommandLineOption<bool>(nameof(NoSplash), "NOSPLASH", false),
            new CommandLineOption<bool>(nameof(NoShow), "NOSHOW", false),
            new CommandLineOption<bool>(nameof(Hidden), "HIDDEN", false),
            new CommandLineArgument<int>(nameof(ApiTcpServerPort), "PORT", 0),
            new CommandLineOption<bool>(nameof(NoDebugOutput), "NOSTDOUT", false),
            new CommandLineOption<bool>(nameof(DoNotUseRecentlyUsedFileList), "SKIPINIRECENT", false),
            new CommandLineOption<bool>(nameof(DoNotUseSettingsFile), "SKIPINI", false),
            new CommandLineOption<bool>(nameof(NoCommunicationToRoboDkServer), "SKIPCOM", false),
            new CommandLineOption<bool>(nameof(ExitRoboDkAfterClosingLastApiConnection), "EXIT_LAST_COM", false),
            new CommandLineOption<bool>(nameof(NoUserInterface), "NOUI", false),
            new CommandLineArgument<int>(nameof(TreeState), "TREE_STATE", 0),

            new CommandLineArgumentDebug(nameof(Logfile), "DEBUG", null),
            new CommandLineArgument<string>(nameof(LoadSettingsFromFile), "SETTINGS", ""),
            new CommandLineOption<bool>(nameof(HideCoordinates), "COORDS_HIDE", false),
            new CommandLineOption<bool>(nameof(HideWindowsWhileLoadingNcFile), "NO_WINDOWS", false),
        };

        // The constructor will put the CommandLineOptions into a dictionary so we can access the options by there property name
        private readonly Dictionary<string, CommandLineOption> _parameterDictionary = new Dictionary<string, CommandLineOption>();

        #endregion

        #region Constructors

        public RoboDkCommandLineParameter()
        {
            // Add the command line options to a dictionary so we can access them easily
            // by the property name.
            foreach (var commandLineOption in _parameterList)
            {
                _parameterDictionary.Add(commandLineOption.PropertyName, commandLineOption);
            }

            // Assumption: CommandLineParameter only make sense when a new RoboDK instance shall be started.
            // Do not try to connect to an existing RoboDK server.
            StartNewInstance = true;

            // Don't relay on the default server port of RoboDK.exe.
            // Request a specific server port.
            ApiTcpServerPort = DefaultApiServerPort;
        }

        #endregion

        #region Properties

        /// <summary>
        /// Hides all windows that are usually shown automatically when loading an NC file.
        /// </summary>
        /// <value>Default:false</value>
        public bool HideWindowsWhileLoadingNcFile
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Loads the arguments from a text file. Each line of that text file is considered as a one single argument.
        /// </summary>
        /// <value>path to settings file. (Default="")</value>
        public string LoadSettingsFromFile
        {
            set => SetOption(value);
            get => GetOption<string>();
        }

        /// <summary>
        /// TODO: Add Comment (ask Albert)
        /// </summary>
        /// <value>True: Hide coordinates (Default=false)</value>
        public bool HideCoordinates
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// TREE_STATE command line option:
        ///
        ///    •	Using state = 0(/ TREE_STATE = 0) is the default option and it is the same as not using it.
        ///    •	Using state = -1 does not display the tree and it is impossible to show the tree from the user point of view
        ///    •	Use state = -2 to not show the main screen. RoboDK runs without a main window and you can only use RoboDK through the API.This may be unsafe and it assumes that RoboDK is operated through the API only.
        ///    •	If / TREE_STATE > 0 the tree will be shown as a docked widget, the bits defined by the integer value are organized as:
        ///
        /// bit 1->ignored
        /// bit 2->The tree is Visible on startup.If this bit is not set, the tree can be shown by right clicking on the toolbar and selecting Tree
        /// bit 3->The tree is Docked on the left(otherwise it is floating)
        /// Some examples to display the tree:
        ///    -> How to set a floating tree, visible:
        ///       RoboDK.exe / TREE_STATE = 2
        ///
        ///    ->How to set a hidden tree, docked on the left
        ///      RoboDK.exe / TREE_STATE = 4
        ///
        ///    ->How to set a visible tree, docked on the left:
        ///      RoboDK.exe / TREE_STATE = 6
        /// </summary>
        /// <value>Tree State option. (Default=0)</value>
        public int TreeState
        {
            set => SetOption(value);
            get => GetOption<int>();
        }

        /// <summary>
        /// Start RoboDK without the User Interface (Window and 3D view).
        /// Use this option to run RoboDK in the background using the API.
        /// It also saves some memory as an OpenGL context is not created.
        /// </summary>
        /// <value>Default:false</value>
        public bool NoUserInterface
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// If set to True, the RoboDK process will terminate itself after the last TCP connection has been closed.
        /// </summary>
        public bool ExitRoboDkAfterClosingLastApiConnection
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// If set to True, RoboDK will not reading the settings.ini file.
        /// The application sets options exclusively through API commands.
        /// </summary>
        public bool DoNotUseSettingsFile
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Do not add any files to the recently used file list.
        /// Without this option each RDK.AddFile() will be added to the recently used RoboDK file list.
        /// (Performance killer!!!)
        /// </summary>
        public bool DoNotUseRecentlyUsedFileList
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Set to True to prevent RoboDK from trying to run the commands on an existing running instance of RoboDK
        /// </summary>
        public bool StartNewInstance
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Set to True to prevent any communication with RoboDK server.
        /// </summary>
        public bool NoCommunicationToRoboDkServer
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Only write to logfile. Disable output to Visual Studio Output Window.
        /// </summary>
        public bool NoDebugOutput
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Forces the API communication through the given port (TCP/IP protocol).
        /// RoboDK opens a listening TCP socket in the given port number and waits for a connection.
        /// </summary>
        /// <value>Default:20500</value>
        public int ApiTcpServerPort
        {
            set => SetOption(value);
            get => GetOption<int>();
        }

        /// <summary>
        /// Don't show RoboDK Window.
        /// </summary>
        public bool StartHidden
        {
            set
            {
                NoSplash = value;
                NoShow = value;
                Hidden = value;
            }
            get => NoSplash && NoShow && Hidden;
        }

        /// <summary>
        /// Removes the RoboDK splash image on start.
        /// </summary>
        /// <value>Default:false</value>
        public bool NoSplash
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Hides all windows while RoboDK is loading files and updating programs.
        /// </summary>
        /// <value>Default:false</value>
        public bool NoShow
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Avoids the automatic /SHOW once RoboDK has finished loading.
        /// The only way of showing the window afterwards is by using the API.
        /// <seealso cref="IRoboDK.SetWindowState"/>
        /// </summary>
        /// <value>Default:false</value>
        public bool Hidden
        {
            set => SetOption(value);
            get => GetOption<bool>();
        }

        /// <summary>
        /// Creates a RoboDK.debug.txt logfile that allows debugging the application.
        /// Logfile:
        ///    - null: no logfile will be written (default)
        ///    - ""  : Enable RoboDK logging. Default logfile: "RoboDK.debug.txt".
        ///    - filename: RoboDK will use the given filename as logfile.
        ///              E.g.: "C:\Temp\MyRoboDK.log"
        ///              This can be useful if more then one roboDK instance is running
        ///              so each RoboDK instance will write it's log messages into it's own Logfile.
        /// </summary>
        public string Logfile
        {
            set => SetOption(value);
            get => GetOption<string>();
        }

        /// <summary>
        /// Iterates through all arguments and puts together a command line string which can be passed
        /// as command line argument string to RoboDK.
        /// </summary>
        public string CommandLineArgumentString
        {
            get
            {
                var args = string.Join(" ", _parameterList
                    .Select(p => p.CommandLineOptionString)
                    .Where(s => !string.IsNullOrWhiteSpace(s))
                    .ToArray());
                return args;
            }
        }

        #endregion

        #region Private Methods

        private void SetOption<T>(T value, [CallerMemberName] string name = "")
        {
            ((CommandLineOption<T>)_parameterDictionary[name]).Value = value;
        }

        private T GetOption<T>([CallerMemberName] string name = "")
        {
            return ((CommandLineOption<T>)_parameterDictionary[name]).Value;
        }

        #endregion
    }


    internal class CommandLineOption
    {
        #region Fields

        internal static string SwitchDelimiter = "-";

        #endregion

        #region Constructors

        internal CommandLineOption(string propertyName, string argument)
        {
            PropertyName = propertyName;
            Argument = argument;
        }

        #endregion

        #region Properties

        internal virtual string CommandLineOptionString => "";

        internal string PropertyName { get; }

        internal string Argument { get; }

        #endregion
    }

    internal class CommandLineOption<T> : CommandLineOption
    {
        #region Constructors

        internal CommandLineOption(string propertyName, string argument, T defaultValue)
            : base(propertyName, argument)
        {
            DefaultValue = defaultValue;
            Value = DefaultValue;

            // TODO: How to define type constraint to class declaration? "where T : IComparable"
            if (!typeof(T).GetInterfaces().Contains(typeof(IComparable)))
            {
                throw new ArgumentException($"Value of command line argument {Argument} is not of type IComparable");
            }
        }

        #endregion

        #region Properties

        internal T Value { get; set; }

        internal T DefaultValue { get; }

        protected bool IsDefault => Equals((IComparable)Value, (IComparable)DefaultValue);

        internal override string CommandLineOptionString => IsDefault ? "" : $"{SwitchDelimiter}{Argument}";

        #endregion
    }

    internal class CommandLineArgument<T> : CommandLineOption<T>
    {
        #region Constructors

        internal CommandLineArgument(string propertyName, string argument, T defaultValue)
            : base(propertyName, argument, defaultValue)
        {
        }

        #endregion

        #region Properties

        internal override string CommandLineOptionString => IsDefault ? "" : $"{SwitchDelimiter}{Argument}={Value.ToString()}";

        #endregion
    }

    internal class CommandLineArgumentDebug : CommandLineOption<string>
    {
        #region Constructors

        internal CommandLineArgumentDebug(string propertyName, string argument, string defaultValue)
            : base(propertyName, argument, defaultValue)
        {
        }

        #endregion

        #region Properties

        internal override string CommandLineOptionString
        {
            get
            {
                if (Value != null)
                {
                    return string.IsNullOrWhiteSpace(Value) ? $"{SwitchDelimiter}{Argument}" : $"{SwitchDelimiter}{Argument}={Value}";
                }

                return "";
            }
        }

        #endregion
    }
}