
// We currently can not support RoboDK Tests on the build server.
// Ignore all tests on the build server
// To locally execute the unit test uncomment the line below
//#define TEST_ROBODK_API

#region Namespaces

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using RoboDk.API;
using RoboDk.API.Exceptions;
using RoboDk.API.Model;


#endregion

namespace RoboDkApiTest
{
#if !TEST_ROBODK_API
    [Ignore]
#endif
    [TestClass]
    public class RoboDkApiTestWhenRoboDkIsRunning
    {
        #region Fields

        private static IRoboDK _roboDk;

        #endregion

        #region Public Methods

        [ClassCleanup]
        public static void Class_Cleanup()
        {
            RoboDkProcessHelper.StopRoboDkInstance();
        }

        [TestInitialize]
        public void Test_Initialize()
        {
            _roboDk = RoboDkProcessHelper.GetExistingRoboDkOrStartNewIfItDoesNotExist();
            _roboDk.CloseStation();
        }

        [TestMethod]
        public void Test_BasicEventListenerApi()
        {
            var rdk = new RoboDK();
            rdk.Connect();

            // Open Event Channel
            var eventListener = rdk.OpenRoboDkEventChannel();
            var noEvent = eventListener.WaitForEvent();
            noEvent.EventType.Should().Be(EventType.NoEvent);

            // Test Simple Event
            var frame1 = rdk.AddFrame("Frame1");
            var itemMovedEvent = eventListener.WaitForEvent();
            itemMovedEvent.EventType.Should().Be(EventType.ItemMovedPose);
            itemMovedEvent.Item.Name().Should().Be("Frame1");

            // The RoboDK link must be set to the RoboDK API instance
            itemMovedEvent.Item.RDK().RoboDKClientPort.Should().Be(rdk.RoboDKClientPort);

            // Open a second event channel
            var eventListener2 = rdk.OpenRoboDkEventChannel();
            var frame2 = rdk.AddFrame("Frame2");
            var eventOnChannel1 = eventListener.WaitForEvent();
            var eventOnChannel2 = eventListener2.WaitForEvent();
            eventOnChannel1.EventType.Should().Be(EventType.ItemMovedPose);
            eventOnChannel1.Item.Name().Should().Be("Frame2");
            eventOnChannel2.EventType.Should().Be(EventType.ItemMovedPose);
            eventOnChannel2.Item.Name().Should().Be("Frame2");
            eventOnChannel1.Item.RDK().RoboDKClientPort.Should().Be(rdk.RoboDKClientPort);
            eventOnChannel2.Item.RDK().RoboDKClientPort.Should().Be(rdk.RoboDKClientPort);

            // After closing an event channel we should get an exception when calling WaitForEvent
            eventListener.Close();
            var whenAction = new Action(() => eventListener.WaitForEvent());
            whenAction.Should().Throw<ObjectDisposedException>();
        }

        [TestMethod]
        public void Test_ConnectDisconnectWhenRoboDKIsAlreadyRunning()
        {
            var rdk = new RoboDK();

            for (var i = 0; i < 10; i++)
            {
                rdk.Connected().Should().BeFalse();
                rdk.Connect().Should().BeTrue();

                // RoboDK is already running. It is not expected that connect will start a new process
                rdk.Process.Should().BeNull();
                rdk.Connected().Should().BeTrue();

                // Test some properties
                rdk.Version().Should().StartWith("5");
                rdk.ApiVersion.Should().BeGreaterThan(0);
                rdk.RoboDKBuild.Should().BeGreaterThan(0);
                rdk.RoboDKServerPort.Should().BeGreaterThan(0);
                rdk.RoboDKClientPort.Should().BeGreaterThan(0);
                rdk.RoboDKServerIpAddress.Length.Should().BeGreaterThan(0);
                rdk.DefaultSocketTimeoutMilliseconds.Should().BeGreaterThan(1000);

                rdk.Disconnect();
                rdk.Connected().Should().BeFalse();
            }
        }

        [TestMethod]
        public void Test_RoboDkThrowsObjectDisposedExceptionWhenCallingConnectAfterDispose()
        {
            // Given
            var rdk = new RoboDK();
            rdk.Connect().Should().BeTrue();

            // When
            rdk.Dispose();

            // Then
            var whenAction = new Action(() => rdk.Connect());
            whenAction.Should().Throw<ObjectDisposedException>();
        }

        [TestMethod]
        public void Test_RoboDkThrowsObjectDisposedExceptionWhenCallingAnApiMethodAfterDispose()
        {
            // Given
            var rdk = new RoboDK();
            rdk.Connect().Should().BeTrue();

            // When
            rdk.Dispose();

            // Then
            var whenAction = new Action(() => rdk.AddFrame("TestFrame"));
            whenAction.Should().Throw<ObjectDisposedException>();
        }

        #endregion
    }

#if !TEST_ROBODK_API
    [Ignore]
#endif
    [TestClass]
    public class RoboDkApiConnectTestWhenStartingNewRoboDKInstance
    {
        #region Public Methods

        [ClassCleanup]
        public static void Class_Cleanup()
        {
            RoboDkProcessHelper.StopRoboDkInstance();
        }

        [TestInitialize]
        public void Test_Initialize()
        {
            RoboDkProcessHelper.StopRoboDkInstance();
        }

        [TestMethod]
        public void Test_DefaultStartAndEndServerPort()
        {
            var rdk = new RoboDK();
            rdk.RoboDKServerStartPort.Should().BeLessOrEqualTo(rdk.RoboDKServerEndPort);
            rdk.RoboDKServerStartPort.Should().Be(rdk.DefaultApiServerPort);
            rdk.RoboDKServerEndPort.Should().Be(rdk.DefaultApiServerPort + 2);
        }

        [TestMethod]
        public void Test_WhenSettingStartServerPortThenEndServerPortMustHaveSameValue()
        {
            var rdk = new RoboDK
            {
                RoboDKServerStartPort = 40000
            };
            rdk.RoboDKServerStartPort.Should().Be(40000);
            rdk.RoboDKServerEndPort.Should().Be(40000);

            rdk = new RoboDK
            {
                RoboDKServerStartPort = 10000
            };
            rdk.RoboDKServerStartPort.Should().Be(10000);
            rdk.RoboDKServerEndPort.Should().Be(10000);
        }

        /// <summary>
        /// Test if RoboDK is handling temporary connections properly.
        /// In the past we had some receive timeout issues when opening a temporary second connection.
        /// </summary>
        [TestMethod]
        public void Test_ParallelRoboDKConnections()
        {
            var stopAsyncTask = false;
            var rdk = new RoboDK
            {
                RoboDKServerStartPort = 10000,
                Logfile = Path.Combine(Directory.GetCurrentDirectory(), "RoboDk.log"),
                DefaultSocketTimeoutMilliseconds = 20*1000
            };

            rdk.Connect();
            rdk.Render(false);
            rdk.Command("AutoRenderDelay", 50);
            rdk.Command("AutoRenderDelayMax", 300);
            rdk.DefaultSocketTimeoutMilliseconds = 10 * 1000;

            List<IItem> AddStaticParts()
            {
                var parts = new List<IItem>();
                var cwd = Directory.GetCurrentDirectory();
                parts.Add(rdk.AddFile(Path.Combine(cwd, "TableOut.sld")));
                parts.Add(rdk.AddFile(Path.Combine(cwd, "robot.robot")));
                return parts;
            }
            List<IItem> AddDynamicParts()
            {
                var parts = new List<IItem>();
                var cwd = Directory.GetCurrentDirectory();
                for (var n = 0; n < 10; n++)
                {
                    parts.Add(rdk.AddFile(Path.Combine(cwd, "Phone Case Box.sld")));
                    parts.Add(rdk.AddFile(Path.Combine(cwd, "Box.sld")));
                    parts.Add(rdk.AddFile(Path.Combine(cwd, "Phone Case Done.sld")));
                }

                return parts;
            }

            // Task which opens a temporary new connection
            void DoTemporaryConnectionCalls(IReadOnlyCollection<IItem> staticParts)
            {
                // ReSharper disable once AccessToModifiedClosure
                while(!stopAsyncTask)
                {
                    foreach (var staticPart in staticParts)
                    {
                        Thread.Sleep(1);
                        using (var roboDkLink = new RoboDK.RoboDKLink(staticPart.RDK()))
                        {
                            var clonedItem = staticPart.Clone(roboDkLink.RoboDK);
                            clonedItem.Pose();
                        }
                    }
                }
            }

            var p = AddStaticParts();
            var task = new Task(() => DoTemporaryConnectionCalls(p));
            task.Start();

            try
            {
                for (var i = 0; i < 20; i++)
                {
                    var dynamicParts = AddDynamicParts();
                    rdk.Command("CollisionMap", "Off");
                    rdk.SetCollisionActive(CollisionCheckOptions.CollisionCheckOff);
                    rdk.Delete(dynamicParts);
                }
            }
            catch (Exception ex)
            {
                Assert.Fail(ex.Message);
            }
            finally
            {
                stopAsyncTask = true;
            }

            try
            {
                task.Wait();
            }
            catch (Exception ex)
            {
                Assert.Fail(ex.Message);
            }
            finally
            {
                rdk.CloseRoboDK();
            }
        }



        [TestMethod]
        public void Test_WhenEndServerPortSmallerThenStartServerPortThenThrowRdkException()
        {
            var rdk = new RoboDK
            {
                RoboDKServerStartPort = 10000,
                RoboDKServerEndPort = 9000
            };
            rdk.RoboDKServerStartPort.Should().Be(10000);
            rdk.RoboDKServerEndPort.Should().Be(9000);

            Action act = () => rdk.Connect();
            act.Should().Throw<RdkException>();
        }

        [TestMethod]
        public void Test_WhenConnectingOnUsedPassiveSocketThenNoConnectionAndRoboDkNotStarted()
        {
            var port = 56252;
            while (!RoboDK.IsTcpPortFree(port))
            {
                port++;
            }

            using (var s = new SocketHelper())
            {
                s.OpenServer(port);
                RoboDK.IsTcpPortFree(s.ServerPort).Should().BeFalse();

                var rdk = new RoboDK
                {
                    RoboDKServerStartPort = port,
                };

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().BeNull();

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().BeNull();

                rdk.Invoking(r => r.CloseRoboDK())
                    .Should().Throw<RdkException>();
            }
        }

        [TestMethod]
        public void Test_WhenConnectingOnUsedActiveSocketThenNoConnectionAndRoboDkNotStarted()
        {
            var port = 56252;
            while (!RoboDK.IsTcpPortFree(port))
            {
                port++;
            }

            using (var s = new SocketHelper())
            {
                s.OpenServerAndClient(port);

                RoboDK.IsTcpPortFree(s.ServerPort).Should().BeFalse();
                RoboDK.IsTcpPortFree(s.ClientPort).Should().BeFalse();

                var rdk = new RoboDK
                {
                    RoboDKServerStartPort = port,
                };

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().BeNull();

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().BeNull();

                rdk.Invoking(r => r.CloseRoboDK())
                    .Should().Throw<RdkException>();
            }
        }

        [TestMethod]
        public void Test_WhenStartingOnUsedPassiveSocketThenNoConnectionAndRoboDkNotStarted()
        {
            var port = 56252;
            while (!RoboDK.IsTcpPortFree(port))
            {
                port++;
            }

            using (var s = new SocketHelper())
            {
                s.OpenServer(port);

                RoboDK.IsTcpPortFree(s.ServerPort).Should().BeFalse();

                var rdk = new RoboDK
                {
                    StartNewInstance = true,
                    RoboDKServerStartPort = port,
                };

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().NotBeNull();
                rdk.Process.HasExited.Should().BeTrue();
                Process.GetProcessesByName("RoboDK").Should().BeEmpty();

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().NotBeNull();
                rdk.Process.HasExited.Should().BeTrue();
                Process.GetProcessesByName("RoboDK").Should().BeEmpty();

                rdk.Invoking(r => r.CloseRoboDK())
                    .Should().Throw<RdkException>();
            }
        }

        [TestMethod]
        public void Test_WhenStartingOnUsedActiveSocketThenNoConnectionAndRoboDkNotStarted()
        {
            var port = 56252;
            while (!RoboDK.IsTcpPortFree(port))
            {
                port++;
            }

            using (var s = new SocketHelper())
            {
                s.OpenServerAndClient(port);

                RoboDK.IsTcpPortFree(s.ServerPort).Should().BeFalse();
                RoboDK.IsTcpPortFree(s.ClientPort).Should().BeFalse();

                var rdk = new RoboDK
                {
                    StartNewInstance = true,
                    RoboDKServerStartPort = port,
                };

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().NotBeNull();
                rdk.Process.HasExited.Should().BeTrue();
                Process.GetProcessesByName("RoboDK").Should().BeEmpty();

                rdk.Connect().Should().BeFalse();
                rdk.Connected().Should().BeFalse();
                rdk.Process.Should().NotBeNull();
                rdk.Process.HasExited.Should().BeTrue();
                Process.GetProcessesByName("RoboDK").Should().BeEmpty();

                rdk.Invoking(r => r.CloseRoboDK())
                    .Should().Throw<RdkException>();
            }
        }

        [TestMethod]
        [Ignore]
        public void Test_CommandLineParameter()
        {
            var rdk = new RoboDK
            {
                ApplicationDir = "C:\\zBuilds\\Bystronic\\repository\\ByRobotManager-2\\ByRobotManager\\bin\\Debug\\RoboDK\\RoboDK.exe",
                RoboDKServerStartPort = 56252,

                //CustomCommandLineArgumentString = "-NOSPLASH -NOSHOW -HIDDEN -PORT=56252  -NOSTDOUT -SKIPINIRECENT -SKIPINI -SKIPCOM -EXIT_LAST_COM -NOUI",
                CustomCommandLineArgumentString = "-PORT=56252  -NOSTDOUT -SKIPINIRECENT -SKIPINI -SKIPCOM -EXIT_LAST_COM -NOUI -TREE_STATE=-1",

                //CustomCommandLineArgumentString = "/NOSPLASH /NOSHOW /HIDDEN /PORT=56252  /NOSTDOUT /SKIPINIRECENT /SKIPINI /SKIPCOM /EXIT_LAST_COM /NOUI /TREE_STATE=-1",
                //CustomCommandLineArgumentString = "/NOSPLASH /NOSHOW /HIDDEN /NOSTDOUT /SKIPINIRECENT /SKIPINI /SKIPCOM /EXIT_LAST_COM /NOUI /TREE_STATE=-1"
                //CustomCommandLineArgumentString = "/NOSTDOUT /SKIPINIRECENT /SKIPINI /SKIPCOM /EXIT_LAST_COM /NOUI"
            };
            rdk.Connect();

//            Thread.Sleep(5000);
            var mainWindow = rdk.Command("MainWindow_ID");

            var item = rdk.AddFile(@"C:\Users\mth\AppData\Local\Temp\ByRobotManager_Geometries\Regrip lower arm NS2+NS3_collision.sld");
            item.SetParam("FilterMesh", "0,0.0001,0.005");

            var mainWindowId = int.Parse(mainWindow);


            rdk.CloseRoboDK();
        }

        #endregion
    }

#if !TEST_ROBODK_API
    [Ignore]
#endif
    [TestClass]
    public class RoboDkApiTest
    {
        #region Fields

        private static IRoboDK _roboDk;

        #endregion

        #region Public Methods

        [ClassCleanup]
        public static void Class_Cleanup()
        {
            RoboDkProcessHelper.StopRoboDkInstance();
        }

        [TestInitialize]
        public void Test_Initialize()
        {
            _roboDk = RoboDkProcessHelper.GetExistingRoboDkOrStartNewIfItDoesNotExist();
            _roboDk.CloseStation();
        }

        [TestMethod]
        public void Test_CopyPasteSingleElement()
        {
            var frame1 = _roboDk.AddFrame("Frame1");
            var frame2 = _roboDk.AddFrame("Frame2", frame1);

            _roboDk.Copy(frame1, copy_children: false);
            var pasteItem = _roboDk.Paste();
            pasteItem.Childs().Should().BeEmpty();
            pasteItem.ItemId.Should().NotBe(frame1.ItemId);
            pasteItem.Name().Should().Be(frame1.Name());
        }

        [TestMethod]
        public void Test_CopyPasteItemTree()
        {
            var frame1 = _roboDk.AddFrame("Frame1");
            var frame2 = _roboDk.AddFrame("Frame2", frame1);

            _roboDk.Copy(frame1, copy_children: true);
            var pasteItem = _roboDk.Paste();
            pasteItem.Childs().Should().HaveCount(1);
            pasteItem.ItemId.Should().NotBe(frame1.ItemId);
            pasteItem.Name().Should().Be(frame1.Name());

            var child = pasteItem.Childs()[0];
            child.ItemId.Should().NotBe(frame2.ItemId);
            child.Name().Should().Be(frame2.Name());
        }

        #endregion
    }


    internal class SocketHelper : IDisposable
    {
        #region Fields

        private Socket _client;
        private Socket _listener;
        private Socket _server;

        #endregion

        #region Properties

        public int ServerPort => ((IPEndPoint)_listener.LocalEndPoint).Port;

        public int ClientPort => ((IPEndPoint)_client.LocalEndPoint).Port;

        #endregion

        #region Public Methods

        public void OpenServer(int serverPort)
        {
            // Establish the local endpoint for the socket.  
            // Dns.GetHostName returns the name of the
            // host running the application.  
            var ipHostInfo = Dns.GetHostEntry("localhost");
            var addressList = ipHostInfo.AddressList.Where(h => h.AddressFamily == AddressFamily.InterNetwork);
            var ipAddress = addressList.First();
            var localEndPoint = new IPEndPoint(ipAddress, serverPort);

            // Create a TCP/IP socket.  
            _listener = new Socket(ipAddress.AddressFamily,
                SocketType.Stream, ProtocolType.Tcp);
            _listener.Bind(localEndPoint);
            _listener.Listen(10);
        }

        public void OpenServerAndClient(int serverPort)
        {
            // Establish the local endpoint for the socket.  
            // Dns.GetHostName returns the name of the
            // host running the application.  
            var ipHostInfo = Dns.GetHostEntry("localhost");
            var addressList = ipHostInfo.AddressList.Where(h => h.AddressFamily == AddressFamily.InterNetwork);
            var ipAddress = addressList.First();
            var localEndPoint = new IPEndPoint(ipAddress, serverPort);

            // Create a TCP/IP socket.  
            _listener = new Socket(ipAddress.AddressFamily,
                SocketType.Stream, ProtocolType.Tcp);
            _listener.Bind(localEndPoint);
            _listener.Listen(10);

            _client = new Socket(ipAddress.AddressFamily,
                SocketType.Stream, ProtocolType.Tcp);
            _client.Connect(localEndPoint);

            _server = _listener.Accept();
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        #endregion

        #region Protected Methods

        protected virtual void Dispose(bool disposing)
        {
            if (disposing)
            {
                _server?.Dispose();
                _client?.Dispose();
                _listener?.Dispose();
            }
        }

        #endregion
    }

    internal static class RoboDkProcessHelper
    {
        #region Constants

        private const string Lock = "lock";

        #endregion

        #region Fields

        private static IRoboDK _roboDk;

        #endregion

        #region Public Methods

        public static void StopRoboDkInstance()
        {
            lock (Lock)
            {
                if (_roboDk != null)
                {
                    _roboDk.CloseRoboDK();
                    _roboDk.Process.WaitForExit(1000);
                    _roboDk = null;
                }
            }

            var roboDKInstances = Process.GetProcessesByName("RoboDK");
            roboDKInstances.Should().BeEmpty("For a successful unit test all existing RoboDK instances must be closed.");
        }

        public static IRoboDK StartNewRoboDkInstance()
        {
            lock (Lock)
            {
                if (_roboDk == null)
                {
                    var roboDKInstances = Process.GetProcessesByName("RoboDK");
                    roboDKInstances.Should().BeEmpty("For a successful unit test all existing RoboDK instances must be closed.");
                }
                else
                {
                    _roboDk.CloseRoboDK();
                    _roboDk.Process.WaitForExit(1000);
                    _roboDk = null;
                }

                _roboDk = new RoboDK();
                _roboDk.Connect().Should().BeTrue();
                return _roboDk;
            }
        }

        public static IRoboDK GetExistingRoboDkOrStartNewIfItDoesNotExist()
        {
            lock (Lock)
            {
                return _roboDk ?? StartNewRoboDkInstance();
            }
        }

        #endregion
    }


    public class ThreadSaveRoboDK
    {

        public static T Invoke<T>(IItem item, Func<IItem, T> func)
        {
            using (var roboDkLink = new RoboDK.RoboDKLink(item.RDK()))
            {
                return func.Invoke(item.Clone(roboDkLink.RoboDK));
            }
        }

        public static void Invoke(IItem item, Action<IItem> action)
        {
            using (var roboDkLink = new RoboDK.RoboDKLink(item.RDK()))
            {
                action.Invoke(item.Clone(roboDkLink.RoboDK));
            }
        }

    }

    internal class Logger
    {
        #region Constants

        private const string Lock = "lock";

        #endregion

        #region Constructors

        #endregion

        #region Public Methods

        public static void WriteLine(string message)
        {
            lock (Lock)
            {
                using (var sw = File.AppendText("unittest.txt"))
                {
                    sw.WriteLine($"{DateTime.Now}: {message}");
                }
            }
        }

        #endregion
    }
}