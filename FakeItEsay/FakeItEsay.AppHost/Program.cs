using Microsoft.Extensions.Hosting;

var builder = DistributedApplication.CreateBuilder(args);
#pragma warning disable ASPIREHOSTINGPYTHON001
var fakeItEasy = builder.AddPythonApp("FakeITEasy", "../../FakeITEasy", "app.py")
    .WithHttpEndpoint(env: "PORT", port: 5001)
    .WithHttpsEndpoint(env: "HTTPS_PORT", port: 5002);
   // .WithExternalHttpEndpoints()
    //.WithOtlpExporter()

var opcua = builder.AddExecutable("OPCUA", "python3", "../../FakeITEasy", ["server.py"]);
   
#pragma warning restore ASPIREHOSTINGPYTHON001

if (builder.ExecutionContext.IsRunMode && builder.Environment.IsDevelopment())
{
    fakeItEasy.WithEnvironment("DEBUG", "True");
   // opcua.WithEnvironment("DEBUG", "True");
}
builder.Build().Run();
